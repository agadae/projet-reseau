import threading
import sys
import os
import pygame as pg
import time
import json
from GameControl.game import Game
from GameControl.EventManager import show_menu
from pygame.locals import *
from GameControl.gameControl import GameControl
from peer_communication import threaded_send, threaded_receive, start_server, start_client
from Tiles.tiles import Tile
sys.path.append("/home/kali/pro/jeu2/")
from Tiles.Bob.bob import Bob



def main(instance_number):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    pg.init()
    screen = pg.display.set_mode((600, 400))
    pg.display.set_caption("Multiplayer Game")
    clock = pg.time.Clock()
    game = Game.getInstance(screen, clock)

    communication_thread = threading.Thread(target=start_communication)
    communication_thread.start()

    game.run()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <instance_number>")
        sys.exit(1)

    instance_number = sys.argv[1]
    input_pipe = f"CTOPYTHON{instance_number}"
    output_pipe = f"PYTHONTOC{instance_number}"

    player_id = int(instance_number)
    bobs = [Bob(player_id=player_id)]

    if instance_number == "0":
        start_server()
        time.sleep(5)
    else:
        time.sleep(2)
        start_client()

    t1 = threading.Thread(target=main, args=(instance_number,))
    t2 = threading.Thread(target=threaded_receive, args=(instance_number, bobs, input_pipe))
    t3 = threading.Thread(target=threaded_send, args=(instance_number, bobs, output_pipe))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

