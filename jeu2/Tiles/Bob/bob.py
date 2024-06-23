from ..tiles import Tile
from GameControl.gameControl import GameControl
from GameControl.setting import Setting
from Tiles.directions import directionsDict, directionsList
from view.texture import *
import random
from math import floor
import json

class Bob:
    id = 0
    def __init__(self, player_id=0):
        self.setting = Setting.getSettings()
        self.id = player_id
        self.age = 0
        self.isHunting = False
        self.alreadyInteracted = False
        self.CurrentTile = None
        self.energy = self.setting.getBobSpawnEnergy()
        self.energyMax = self.setting.getBobMaxEnergy()
        self.mass = self.setting.getDefaultMass()
        self.velocity = self.setting.getDefaultVelocity()
        self.speedBuffer = 0
        self.speed = self.velocity
        self.vision = self.setting.getDefaultVision()
        self.NextTile = None
        self.predators = []
        self.prey = None
        self.foodTilesInVision = []
        self.memoryPoint = self.setting.getDefaultMemoryPoint()
        self.memorySpace = 2 * round(self.memoryPoint)
        self.memorySpaceLeft = self.memorySpace
        self.visitedTiles = []
        self.foodTilesInMemo = {}
        self.PreviousTiles = []

    def action(self):
        print(f"Bob {self.id} action started")
        self.PreviousTile = self.CurrentTile
        self.PreviousTiles.append(self.CurrentTile)
        print(f"Bob {self.id} CurrentTile: {self.CurrentTile}")

        if self.energy <= 0: 
            self.die()
        elif self.setting.getSelfReproduction() and self.energy >= self.setting.getBobMaxEnergy():
            self.reproduce()
        else:
            self.consumePerceptionAndMemoryEnergy()
            if self.speed < 1 or self.CurrentTile.getEnergy() != 0 or self.detectPreys(self.CurrentTile.getBobs()) != []:
                self.consumeStationaryEnergy()
                self.interact()
            else:
                self.consumeKinecticEnergy()
                for _ in range(floor(self.speed)):
                    if self in GameControl.getInstance().getDiedQueue():
                        break
                    else:
                        if self.alreadyInteracted:
                            self.alreadyInteracted = False
                            break
                        else:
                            if self.memoryPoint != 0:
                                self.memorizeVisitedTile(self.CurrentTile)
                            if round(self.vision) != 0:
                                self.scan()
                            self.determineNextTile()
                            self.move()
                            self.PreviousTiles.append(self.CurrentTile)
                            self.interact()
            self.updateSpeed()
        for tile in self.CurrentTile.getNearbyTiles(round(self.vision)):
            tile.seen = True
        print(f"Bob {self.id} action completed")


    def spawn(self, tile: Tile):
        self.CurrentTile = tile
        self.PreviousTile = self.CurrentTile
        self.PreviousTiles.append(self.CurrentTile)
        self.CurrentTile.addBob(self)
        GameControl.getInstance().addToNewBornQueue(self)

    def to_dict(self):
        return {
            'id': self.id,
            'age': self.age,
            'isHunting': self.isHunting,
            'alreadyInteracted': self.alreadyInteracted,
            'CurrentTile': self.CurrentTile.id if self.CurrentTile else None,
            'energy': self.energy,
            'energyMax': self.energyMax,
            'mass': self.mass,
            'velocity': self.velocity,
            'speedBuffer': self.speedBuffer,
            'speed': self.speed,
            'vision': self.vision,
            'NextTile': self.NextTile.id if self.NextTile else None,
            'predators': [pred.id for pred in self.predators],
            'prey': self.prey.id if self.prey else None,
            'foodTilesInVision': [tile.id for tile in self.foodTilesInVision],
            'memoryPoint': self.memoryPoint,
            'memorySpace': self.memorySpace,
            'memorySpaceLeft': self.memorySpaceLeft,
            'visitedTiles': [tile.id for tile in self.visitedTiles],
            'foodTilesInMemo': {tile.id: energy for tile, energy in self.foodTilesInMemo.items()},
            'PreviousTiles': [tile.id for tile in self.PreviousTiles]
        }

    @classmethod
    def from_dict(cls, data, tile_map):
        bob = cls(player_id=data['id'])
        bob.age = data['age']
        bob.isHunting = data['isHunting']
        bob.alreadyInteracted = data['alreadyInteracted']
        bob.CurrentTile = tile_map[data['CurrentTile']] if data['CurrentTile'] else None
        bob.energy = data['energy']
        bob.energyMax = data['energyMax']
        bob.mass = data['mass']
        bob.velocity = data['velocity']
        bob.speedBuffer = data['speedBuffer']
        bob.speed = data['speed']
        bob.vision = data['vision']
        bob.NextTile = tile_map[data['NextTile']] if data['NextTile'] else None
        bob.predators = [Bob.getBobById(pred_id) for pred_id in data['predators']]
        bob.prey = Bob.getBobById(data['prey']) if data['prey'] else None
        bob.foodTilesInVision = [tile_map[tile_id] for tile_id in data['foodTilesInVision']]
        bob.memoryPoint = data['memoryPoint']
        bob.memorySpace = data['memorySpace']
        bob.memorySpaceLeft = data['memorySpaceLeft']
        bob.visitedTiles = [tile_map[tile_id] for tile_id in data['visitedTiles']]
        bob.foodTilesInMemo = {tile_map[tile_id]: energy for tile_id, energy in data['foodTilesInMemo'].items()}
        bob.PreviousTiles = [tile_map[tile_id] for tile_id in data['PreviousTiles']]
        return bob

    @staticmethod
    def getBobById(bob_id):
        for bob in GameControl.getInstance().getListBobs():
            if bob.id == bob_id:
                return bob
        return None

    def determineNextTile(self):
        if self.CurrentTile is None:
            print("CurrentTile is None, selecting a random nearby tile.")
            self.CurrentTile = random.choice(self.getNearbyTiles())
        
        print(f"CurrentTile: ({self.CurrentTile.gridX}, {self.CurrentTile.gridY})")
        
        nearbyTiles = self.CurrentTile.getNearbyTiles(1)
        print(f"Nearby Tiles before removal: {[f'({tile.gridX}, {tile.gridY})' for tile in nearbyTiles]}")

        # Vérifiez si la tuile actuelle est dans nearbyTiles avant de la retirer
        if self.CurrentTile in nearbyTiles:
            nearbyTiles.remove(self.CurrentTile)
            print(f"Nearby Tiles after removal: {[f'({tile.gridX}, {tile.gridY})' for tile in nearbyTiles]}")
        else:
            print(f"Warning: CurrentTile ({self.CurrentTile.gridX}, {self.CurrentTile.gridY}) not in nearbyTiles")

        if not nearbyTiles:
            self.NextTile = self.CurrentTile
            print("No nearby tiles, staying on CurrentTile.")
        else:
            nearbyTiles = list(set(nearbyTiles) - set(self.visitedTiles))
            if nearbyTiles:
                self.NextTile = random.choice(nearbyTiles)
            else:
                self.NextTile = self.setRandomTile()
            print(f"NextTile: ({self.NextTile.gridX}, {self.NextTile.gridY})")
        self.isHunting = False

    def move(self):
        self.CurrentTile.removeBob(self)
        self.NextTile.addBob(self)
        self.CurrentTile = self.NextTile

    def updateSpeed(self):
        self.speedBuffer = round(self.speed - floor(self.speed), 2)
        self.speed = self.velocity + self.speedBuffer

################## Consume Energy ##################################
    def consumeKinecticEnergy(self):
        kinecticEnergy = self.mass * self.velocity**2
        self.energy = max(0, round(self.energy - kinecticEnergy, 2))

    def consumePerceptionAndMemoryEnergy(self):
        perceptionEnergy = self.vision * (self.setting.getPerceptionFlatPenalty())
        memoryEnergy = self.memoryPoint * (self.setting.getMemoryFlatPenalty())
        self.energy = max(0, round(self.energy - perceptionEnergy - memoryEnergy, 2)) 

    def consumeStationaryEnergy(self):
        self.energy = max(0, round(self.energy - self.setting.getBobStationaryEnergyLoss(), 2)) 

##################### Interact in one tick  #############################
    def interact(self):
        if (self.CurrentTile.getEnergy() != 0):
            self.consumeFood()
        elif (len(self.CurrentTile.getBobs()) > 1):
            preys = self.detectPreys(self.CurrentTile.getBobs())
            unluckyBob = self.getSmallestPrey(preys)
            if (unluckyBob is not None):
                self.eat(unluckyBob)
            elif (self.setting.getSexualReproduction()):
                partners = self.detectPotentialPartners(self.CurrentTile.getBobs())
                if (partners != []):
                    partner = self.getRandomPartner(partners)
                    self.mate(partner)

##################### Interact with foods #####################################
    def consumeFood(self):
        energy = self.CurrentTile.getEnergy()
        if(self.energy < self.setting.getBobMaxEnergy()):
            if ( self.energy + energy < self.setting.getBobMaxEnergy()):
                self.energy += energy
                self.CurrentTile.foodEnergy = 0
            else:
                self.CurrentTile.foodEnergy -= (self.setting.getBobMaxEnergy() - self.energy)
                self.energy = self.setting.getBobMaxEnergy()
        self.alreadyInteracted = True

################### Interact with other bobs ###########################
    def canEat(self, bob: 'Bob') -> bool:
        return bob.mass * 3 / 2 < self.mass
    
    def eat(self, bob: 'Bob'):
        bob.PreviousTile = bob.CurrentTile
        self.energy = min(self.setting.getBobMaxEnergy(), self.energy + 1/2 * bob.energy * (1 - bob.mass / self.mass))
        bob.die()
        self.alreadyInteracted = True

    def canMate(self, bob: 'Bob') -> bool:
        energyCondition = self.energy >= self.setting.getBobSexualReproductionLevel() and bob.energy >= self.setting.getBobSexualReproductionLevel()
        return energyCondition and not self.canEat(bob) and not bob.canEat(self)

    def mate(self, partner: 'Bob'):
        childBob = Bob()
        childBob.energy = self.setting.getSexualBornEnergy()
        childBob.mass = round((self.mass + partner.mass) / 2, 2)
        childBob.velocity = round((self.velocity + partner.velocity) / 2)
        childBob.speed = childBob.velocity
        childBob.vision = round((self.vision + partner.vision) / 2, 2)
        childBob.memoryPoint = round((self.memoryPoint + partner.memoryPoint) / 2, 2)
        childBob.spawn(self.CurrentTile)
        self.energy -= self.setting.getBobSexualReproductionLoss()
        partner.energy -= self.setting.getBobSexualReproductionLoss()
        self.alreadyInteracted = True
        partner.alreadyInteracted = True
        print("Bob ", self.id, " and Bob ", partner.id, " have a child Bob ", childBob.id)

####################### Detect Preys, Predators. Partners and Foods #####################################
    def detectPreys(self, listBobs: list['Bob']) -> list['Bob']:
        preys : list['Bob'] = []
        for bob in listBobs:
            if (self.canEat(bob)):
                preys.append(bob)
        return preys
    
    def getSmallestPrey(self, listPreys: list['Bob']) -> 'Bob':
        if (listPreys != []):
            smallestMassBob = min(listPreys, key = lambda bob: bob.mass)
            return smallestMassBob
        else:
            return None
        
    def detectPredators(self, listBobs: list['Bob']) -> list['Bob']:
        predators : list['Bob'] = []
        for bob in listBobs:
            if (bob.canEat(self)):
                predators.append(bob)
        return predators
    
    def getClosestPredator(self, listPredators: list['Bob']) -> 'Bob':  
        if (listPredators != []):
            closestPredator = min(listPredators, 
                                 key = lambda bob: Tile.distanceofTile(self.getCurrentTile(), bob.getCurrentTile()))
            return closestPredator
        else:
            return None
    
    def detectPotentialPartners(self, listBobs: list['Bob']) -> list['Bob']:
        potentialPartners: list['Bob'] = []
        for bob in listBobs:
            if (self.canMate(bob) and bob != self):
                potentialPartners.append(bob)
        return potentialPartners
    
    def getRandomPartner(self, listPartners: list['Bob']) -> 'Bob':
        return random.choice(listPartners)
    
    def getLargestNearestFoodTile(self, listFoodTiles: list['Tile']) -> Tile:
        if (listFoodTiles == []):
            return None
        else:
            bestFoodTile = min(listFoodTiles, 
                            key = lambda tile: (Tile.distanceofTile(self.CurrentTile, tile), 
                                                 -tile.getEnergy()))
            return bestFoodTile
        
################ Scan ###########################################
    def scan(self):
        tilesInVision = self.CurrentTile.getNearbyTiles(round(self.vision))

        seenBobs: list['Bob'] = []
        newFoodTilesInVision: list['Tile'] = []

        #remove the food in memo if it in vision right now
        for tile in list(self.foodTilesInMemo.keys()):
            if (Tile.distanceofTile(self.CurrentTile, tile) <= round(self.vision)):
                self.removeFoodTileInMemo(tile)

        #detect bobs and food in vision
        for tile in tilesInVision:
            if (tile.getBobs() != []):
                for bob in tile.getBobs():
                    if (bob != self):
                        seenBobs.append(bob)
            else:
                if (tile.getEnergy() != 0):
                    newFoodTilesInVision.append(tile)

        #remember the food in the precendent tick 
        if (self.memoryPoint != 0):
            notChosenFoods = list(set(self.foodTilesInVision) - set(newFoodTilesInVision))
            for tile in notChosenFoods:
                self.memorizeFoodTile(tile)
        
        #update the food in vision
        self.foodTilesInVision = newFoodTilesInVision.copy()
        
        #detect predators and preys
        self.predators = self.detectPredators(seenBobs)
        
        preysInVision = self.detectPreys(seenBobs)
        self.prey = self.getSmallestPrey(preysInVision)


################ Use memory #####################################
    def memorizeVisitedTile(self, tile: 'Tile'):
        if (tile not in self.visitedTiles):
            if (self.memorySpaceLeft >= 1):
                self.visitedTiles.append(tile)
            else:
                if (self.visitedTiles != []):
                    self.visitedTiles.pop(0)
                self.visitedTiles.append(tile)
        self.updateMemorySpaceLeft()
    
    def memorizeFoodTile(self, tile: 'Tile'):
        if (self.memorySpaceLeft >= 2 ):
            self.foodTilesInMemo[tile] = tile.getEnergy()
        else:
            if (len(self.visitedTiles) >= 2):
                self.visitedTiles.pop(0)
                self.visitedTiles.pop(0)
                self.foodTilesInMemo[tile] = tile.getEnergy()
            else:
                if (self.foodTilesInMemo != {}):
                    smallestFoodtile = min(self.foodTilesInMemo, key = lambda tile: self.foodTilesInMemo[tile])
                    if tile.getEnergy() > self.foodTilesInMemo[smallestFoodtile]:
                        self.foodTilesInMemo.pop(smallestFoodtile)
                self.foodTilesInMemo[tile] = tile.getEnergy()
        self.updateMemorySpaceLeft()

    def updateMemorySpaceLeft(self):
        memorySpaceUsed = len(self.visitedTiles) + 2*len(self.foodTilesInMemo)
        self.memorySpaceLeft = self.memorySpace - memorySpaceUsed
    
    def removeFoodTileInMemo(self, tile: 'Tile'):
        if (tile in self.foodTilesInMemo):
            self.foodTilesInMemo.pop(tile)
            self.updateMemorySpaceLeft()

######################## Find next tile #####################################
    def determineNextTile(self):
        if (self.predators != []):
            self.NextTile = self.runFrom(self.predators)
            self.isHunting = False
        elif (self.foodTilesInVision != []):
            target = self.getLargestNearestFoodTile(self.foodTilesInVision)
            self.NextTile = self.moveToward(target)
            self.isHunting = False
        elif (self.prey is not None):
            target = self.prey.getCurrentTile()
            self.NextTile = self.moveToward(target)
            self.isHunting = True
        elif (self.foodTilesInMemo != {}):
            target = max(self.foodTilesInMemo, key = lambda tile: self.foodTilesInMemo[tile])
            self.NextTile = self.moveToward(target)
            self.isHunting = False
        else:
            # move random but not move to the previous tile
            nearbyTiles = self.CurrentTile.getNearbyTiles(1)
            if self.CurrentTile in nearbyTiles:
                nearbyTiles.remove(self.CurrentTile)
            nearbyTiles = list(set(nearbyTiles) - set(self.visitedTiles))
            self.NextTile = random.choice(nearbyTiles) if nearbyTiles != [] else self.setRandomTile()
            self.isHunting = False

######################## Move toward food, prey ###############################################
    def moveToward(self, target: 'Tile'):

        (x, y) = Tile.CountofTile(target, self.CurrentTile)

        x_direction = 0 if x == 0 else (1 if x > 0 else -1)
        y_direction = 0 if y == 0 else (1 if y > 0 else -1)

        if (x_direction == 0 and y_direction == 0):
            return self.CurrentTile
        else:
            chosenDirection = random.choice(directionsDict[(x_direction, y_direction)])
            return self.CurrentTile.getDirectionTiles(chosenDirection)
    
############################# Run from predators###########################################
    def runFrom(self, predators: list['Bob']):
        bestDirection = None
        bestDistance = 0

        for direction in directionsList:
            tile = self.CurrentTile.getDirectionTiles(direction)
            if tile is None:
                continue
    
            minDistance = min([Tile.distanceofTile(tile, predator.CurrentTile) for predator in predators])
            if minDistance > bestDistance:
                bestDirection = direction
                bestDistance = minDistance
        
        return self.CurrentTile.getDirectionTiles(bestDirection) if bestDirection is not None else self.CurrentTile
    

    def setRandomTile(self):     
        nearbyTiles = self.CurrentTile.getNearbyTiles(1)
        return random.choice(nearbyTiles)

    def randomAdjacent(self):
        nearbyTiles = self.CurrentTile.getNearbyTiles(1)
        if self.CurrentTile in nearbyTiles:
            nearbyTiles.remove(self.CurrentTile)
        return random.choice(nearbyTiles)
        
    def getExplodeTexture(self, progression):
        return loadExplosionImage()[progression]

    def getSpawnTexture(self, progression):
        return loadSpawnImage()[progression]

    def getCurrentTile(self) -> Tile:
        return self.CurrentTile

    def getNextTile(self) -> Tile:
        return self.NextTile

    def getPreviousTile(self) -> Tile:
        return self.PreviousTile

    def getPreviousTiles(self) -> list['Tile']:
        return self.PreviousTiles

    def clearPreviousTiles(self):
        self.PreviousTiles.clear()

    def getEnergy(self) -> float:
        return self.energy

    def getMass(self) -> float:
        return self.mass

    def getVelocity(self) -> float:
        return self.velocity

    def getVision(self) -> float:
        return self.vision

    def getMemoryPoint(self) -> float:
        return self.memoryPoint

    def getId(self) -> int:
        return self.id
    
    def setId(self, id: int):
        self.id = id

    def setEnergy(self, energy: float):
        self.energy = energy

    def setMass(self, mass: float):
        self.mass = mass

    def setVelocity(self, velocity: float):
        self.velocity = velocity

    def setVision(self, vision: float):
        self.vision = vision

    def setMemoryPoint(self, memoryPoint: float):
        self.memoryPoint = memoryPoint

    def setCurrentTile(self, tile: Tile):
        self.CurrentTile = tile

    def setPreviousTile(self, tile: Tile):
        self.PreviousTile = tile