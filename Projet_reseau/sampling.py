from GameControl.setting import Setting
from GameControl.gameControl import GameControl

setting = Setting.getSettings()
gameController = GameControl.getInstance()

class Sampling:
    instance = None
    def __init__(self):
        self.nbBob = gameController.getNbBobs()

    def sample(self):
        print(self.nbBob) 
            
    @staticmethod
    def getSampling():
        Sampling.instance = Sampling()
        return Sampling.instance