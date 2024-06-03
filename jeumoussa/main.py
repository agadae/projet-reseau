import pygame as pg
from GameControl.game import Game
from GameControl.EventManager import show_menu
from pygame.locals import *
from GameControl.setting import Setting
screen = pg.display.set_mode((1920,1080))
flags = HWSURFACE | DOUBLEBUF
header_format = "!I"  # "I" représente un entier non signé de 4 octets

def main():

    pg.init()
    pg.mixer.init()
    screen = pg.display.set_mode((1920,1080))
    clock = pg.time.Clock()
    setting = Setting.getSettings()
    i = show_menu(screen, clock)
    game = Game.getInstance(screen, clock)
    if i == 0:
        game.createNewGame()
    else:
        game.loadGame(i)

    running = True
    playing = True
    while running:
        while playing:
            game.run()
            clock.tick(5*setting.getFps())

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                
if __name__ == "__main__":
    main()
