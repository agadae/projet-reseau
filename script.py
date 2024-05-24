from genericpath import exists
import os
import threading

from genericpath import exists
import os
import threading
from  variable import *


def handle_recv():
    input_pipe = "/home/kali/Desktop/reseau_/vrai_reseau2/CTOPYTHON"
    # os.mkfifo(input_pipe)
    while (True):
        fifo = os.open(input_pipe, os.O_RDONLY)
        str = os.read(fifo, 500)
        str = str.decode('utf-8')
        #print("voici la valeur de stri", str)
        variable.stri = str
    # fifo.close()


def handle_send(param):
    path = "/home/kali/Desktop/reseau_/vrai_reseau2/PYTHONTOC"
    #os.mkfifo(path)

    fifo=open(path,'w')
    string=param
    string = string
    print("valeur envoyé",string)
    fifo.write(string)
    #print('sent to c')

    #fifo.close()
