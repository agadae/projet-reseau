import threading
import time
from peer_communication import handle_recv, handle_send

def main():
    while True:
        print("Main function running...")
        time.sleep(2)

if __name__ == "__main__":
    t1 = threading.Thread(target=main)
    t2 = threading.Thread(target=handle_recv)
    t3 = threading.Thread(target=handle_send)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
