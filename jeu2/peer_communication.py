import socket
import subprocess
import threading
import time
import json
import sys
from GameControl.gameControl import GameControl
from Tiles.tiles import Tile
sys.path.append("/home/kali/pro/jeu/")
from Tiles.Bob.bob import Bob


def send_message(host='localhost', port=9000, message='Hello Server'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)  # Timeout pour la connexion
        try:
            s.connect((host, port))
            s.sendall(message.encode())
            response = s.recv(4096)
            print('Received:', response.decode())
        except socket.timeout:
            print("Connection timeout")
        except ConnectionRefusedError:
            print("Connection refused, retrying...")
            time.sleep(2)  # Attendre avant de réessayer
            send_message(host, port, message)

def receive_message(host='localhost', port=9000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(4096).decode()
                    if not data:
                        break
                    print('Message from client:', data)
                    return data

def threaded_receive(instance_number, bobs, input_pipe):
    port = 9000 + int(instance_number)
    while True:
        try:
            data = receive_message(port=port)  # Utilisez des ports différents pour chaque instance
            if data:
                print(f"Received data: {data}")
                if data.strip():
                    try:
                        game_state = json.loads(data)
                        print(f"Parsed JSON: {game_state}")
                        game_control = GameControl.getInstance()

                        if game_control.getMap() is not None:
                            tile_map = {tile.id: tile for row in game_control.getMap() for tile in row}
                            bobs.clear()
                            for bob_data in game_state:
                                bob = Bob.from_dict(bob_data, tile_map)
                                bobs.append(bob)
                        else:
                            print("Error: The grid is not initialized.")
                    except json.JSONDecodeError:
                        print("Received data is not valid JSON.")
                else:
                    print("Received data is empty or whitespace.")
        except Exception as e:
            print(f"Error in receive thread: {e}")
        time.sleep(1)


def threaded_send(instance_number, bobs, output_pipe):
    while True:
        game_state = json.dumps([bob.to_dict() for bob in bobs])
        send_message(message=game_state)
        time.sleep(1)  # Fréquence d'envoi, ajustez selon le besoin du jeu







def start_server():
    subprocess.Popen(['./peers'])

def start_client():
    subprocess.Popen(['./peerc'])

# Threaded functions to handle sending and receiving
# def threaded_send(instance_number, bobs, output_pipe):
#     while True:
#         game_state = json.dumps([bob.__dict__ for bob in bobs])
#         send_message(message=game_state)
#         time.sleep(1)

# def threaded_receive(instance_number, bobs, input_pipe):
#     while True:
#         receive_message()
#         time.sleep(1)
