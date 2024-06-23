
import os

os.mkfifo("PYTHONTOC")
os.mkfifo("CTOPYTHON")

# execute python3 createpipe.py it will create pipe files and then put them in the two folders