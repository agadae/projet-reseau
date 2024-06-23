from typing import TYPE_CHECKING
from GameControl.setting import Setting
import matplotlib.pyplot as plt
import random

if TYPE_CHECKING:
    from Tiles.Bob.bob import Bob
    from Tiles.tiles import Tile

class GameControl:
    instance = None

    def __init__(self):
        self.setting = Setting.getSettings()
        self.grid: list[list['Tile']] = None
        self.nbBobs: int = 0
        self.nbBobsSpawned = 0
        self.listBobs: list['Bob'] = []
        self.listFoods: set['Tile'] = set()
        self.newBornQueue: list['Bob'] = []
        self.diedQueue: list['Bob'] = []
        self.nbDied: int = 0
        self.nbBorn: int = 0
        self.currentTick = 0
        self.currentDay = 0
        self.renderTick = 0
        self.graphData = []
        self.diedData = []
        self.massData = []
        self.bornData = []
        self.veloceData = []
        self.energyData = []
        self.visionData = []
        self.toto_tick = 0
        self.nbMass = 0
        self.nbVeloce = 0
        self.nbVision = 0
        self.nbEnergy = 0

    def getTileById(self, tile_id):
        for row in self.grid:
            for tile in row:
                if tile.id == tile_id:
                    return tile
        return None
    
    def getBobById(self, bob_id):
        for bob in self.listBobs:
            if bob.id == bob_id:
                return bob
        return None

    def getMasses(self) -> list[float]:
        return [bob.getMass() for bob in self.getListBobs()]
    
    def getVeloce(self) -> list[float]:
        return [bob.getVelocity() for bob in self.getListBobs()]
    
    def getVision(self) -> list[float]:
        return [bob.getVision() for bob in self.getListBobs()]
    
    def getEnergies(self) -> list[float]:
        return [bob.getEnergy() for bob in self.getListBobs()]
    
    def updateMassData(self):
        masses = self.getMasses()
        masse_moyenne = sum(masses) / len(masses) if masses else 0
        self.nbMass = masse_moyenne
        self.massData.append((self.toto_tick, masse_moyenne))

    def updateVeloceData(self):
        veloce = self.getVeloce()
        veloce_moyenne = sum(veloce) / len(veloce) if veloce else 0
        self.nbVeloce = veloce_moyenne
        self.veloceData.append((self.toto_tick, veloce_moyenne))

    def updateVisionData(self):
        vision = self.getVision()
        vision_moyenne = sum(vision) / len(vision) if vision else 0
        self.nbVision = vision_moyenne
        self.visionData.append((self.toto_tick, vision_moyenne))

    def updateEnergyData(self):
        energies = self.getEnergies()
        energy_moyenne = sum(energies) / len(energies) if energies else 0
        self.nbEnergy = energy_moyenne
        self.energyData.append((self.toto_tick, energy_moyenne))
    
    def initiateGame(self):
        self.setting = Setting.getSettings()
        self.grid = None
        self.nbBobs = 0
        self.nbBobsSpawned = 0
        self.listBobs = []
        self.listFoods = set()
        self.newBornQueue = []
        self.diedQueue = []
        self.currentTick = 0
        self.currentDay = 0
        self.renderTick = 0
        self.graphData = []
        self.diedData = []
        self.massData = []
        self.bornData = []
        self.veloceData = []
        self.energyData = []
        self.visionData = []
        self.toto_tick = 0        
        self.nbMass = 0
        self.nbVeloce = 0
        self.nbVision = 0
        self.nbEnergy = 0

    def setMap(self, map):
        self.grid = map

    def getMap(self):
        return self.grid

    def getNbBobs(self):
        return self.nbBobs

    def setNbBobs(self, nbBobs):
        self.nbBobs = nbBobs

    def getNbBorn(self):
        return self.nbBorn

    def setNbBorn(self, nbBorn):
        self.nbBorn = nbBorn

    def getNbDied(self):
        return self.nbDied

    def setNbDied(self, nbDied):
        self.nbDied = nbDied

    def getNbMass(self):
        return self.nbMass

    def setNbMass(self, nbMass):
        self.nbMass = nbMass

    def getListBobs(self):
        return self.listBobs

    def getNbBobsSpawned(self):
        return self.nbBobsSpawned

    def setNbBobsSpawned(self, nbBobsSpawned):
        self.nbBobsSpawned = nbBobsSpawned

    def getNewBornQueue(self):
        return self.newBornQueue

    def getFoodTiles(self) -> list['Tile']:
        foodTiles = []
        for row in self.getMap():
            for tile in row:
                if tile.getEnergy() > 0:
                    foodTiles.append(tile)
        return foodTiles

    def initiateBobs(self, nbBobs):
        from Tiles.Bob.bob import Bob
        for _ in range(nbBobs):
            print("Adding bob")
            x = random.randint(0, self.setting.getGridLength() - 1)
            y = random.randint(0, self.setting.getGridLength() - 1)
            tile = self.getMap()[x][y]
            bob = Bob()
            bob.spawn(tile)

    def eatingTest(self):
        from Tiles.Bob.bob import Bob
        x1 = random.randint(0, self.setting.getGridLength() - 1)
        y1 = random.randint(0, self.setting.getGridLength() - 1)
        tile1 = self.getMap()[x1][y1]
        bob1 = Bob()
        bob1.spawn(tile1)
        bob1.mass = 2
        bob1.velocity = 1.5
        x2 = random.randint(0, self.setting.getGridLength() - 1)
        y2 = random.randint(0, self.setting.getGridLength() - 1)
        tile2 = self.getMap()[x2][y2]
        bob2 = Bob()
        bob2.spawn(tile2)
        bob2.mass = 1
        bob2.velocity = 1
        x3 = random.randint(0, self.setting.getGridLength() - 1)
        y3 = random.randint(0, self.setting.getGridLength() - 1)
        tile3 = self.getMap()[x3][y3]
        bob3 = Bob()
        bob3.spawn(tile3)
        bob3.mass = 4
        bob3.velocity = 2

    def pushToList(self):
        for bob in self.newBornQueue:
            self.listBobs.append(bob)
            self.nbBobs += 1
            self.nbBobsSpawned += 1
        self.newBornQueue.clear()

    def addToNewBornQueue(self, bob: 'Bob'):
        self.newBornQueue.append(bob)
        self.nbBorn += 1

    def addToDiedQueue(self, bob: 'Bob'):
        self.diedQueue.append(bob)

    def wipeBobs(self):
        for bob in self.diedQueue:
            self.listBobs.remove(bob)
            self.nbBobs -= 1
            self.nbDied += 1
        self.diedQueue.clear()

    def createWorld(self, lengthX, lengthY):
        from Tiles.tiles import Tile
        world = []
        for i in range(lengthX):
            world.append([])
            for j in range(lengthY):
                tile = Tile(gridX=i, gridY=j)
                world[i].append(tile)
        self.setMap(world)

    def wipeFood(self):
        for tile in self.listFoods:
            tile.removeFood()
        self.listFoods.clear()

    def respawnFood(self):
        for _ in range(self.setting.getNbSpawnFood()):
            x = random.randint(0, self.setting.getGridLength() - 1)
            y = random.randint(0, self.setting.getGridLength() - 1)
            self.getMap()[x][y].spawnFood()
            self.listFoods.add(self.getMap()[x][y])

    def updateRenderTick(self):
        self.renderTick += 1
        if self.renderTick == self.setting.getFps():
            self.renderTick = 0
            self.increaseTick()

    def increaseTick(self):
        for row in self.grid:
            for tile in row:
                tile.seen = False
        self.bornData.append((self.toto_tick, self.nbBorn))
        self.nbBorn = 0
        self.pushToList()
        self.wipeBobs()
        self.listBobs.sort(key=lambda x: x.speed, reverse=True)
        for bob in self.listBobs:
            bob.clearPreviousTiles()
        for bob in self.listBobs:
            if bob not in self.diedQueue:
                bob.action()
        self.currentTick += 1
        self.graphData.append((self.toto_tick, self.nbBobs))
        self.diedData.append((self.toto_tick, self.nbDied))
        self.nbDied = 0
        self.massData.append((self.toto_tick, self.nbMass))
        self.veloceData.append((self.toto_tick, self.nbVeloce))
        self.visionData.append((self.toto_tick, self.nbVision))
        self.energyData.append((self.toto_tick, self.nbEnergy))
        self.updateEnergyData()
        self.updateMassData()
        self.updateVeloceData()
        self.updateVisionData()
        self.toto_tick += 1
        if self.currentTick == self.setting.getTicksPerDay():
            self.currentTick = 0
            self.increaseDay()

    def increaseDay(self):
        self.wipeFood()
        self.respawnFood()
        self.currentDay += 1
        self.graphData.append((self.toto_tick, self.nbBobs))
        self.diedData.append((self.toto_tick, self.nbDied))
        self.massData.append((self.toto_tick, self.nbMass))
        self.bornData.append((self.toto_tick, self.nbBorn))
        self.veloceData.append((self.toto_tick, self.nbVeloce))

    def getRenderTick(self):
        return self.renderTick

    def getTick(self):
        return self.currentTick

    def setTick(self, tick):
        self.currentTick = tick

    def getDay(self):
        return self.currentDay

    def setDay(self, day):
        self.currentDay = day

    def getDiedQueue(self):
        return self.diedQueue

    @staticmethod
    def getInstance():
        if GameControl.instance is None:
            GameControl.instance = GameControl()
        return GameControl.instance
