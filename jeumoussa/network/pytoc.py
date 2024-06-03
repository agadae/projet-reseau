



import os


class Packet():
	def __init__(self, ID, IO, PNAME, data):
		self.ID = ID
		self.IO = IO
		self.PNAME = PNAME
		self.data = data



	def stringify(self):
		# Return a string of a packet
		# Field separator is \t
		# Packet separator is \n
		# Data separator is ;
		return str(str(self.ID)+"\t"+str(self.IO)+"\t"+str(self.PNAME)+"\t"+str(self.data)+"\n")

def packetify(packetString):
	tab = str(packetString).split("\t")
	diff = 4 - len(tab)
	for i in range(max(diff, 0)) :
		tab.append("")
	return Packet(tab[0], tab[1], tab[2], tab[3])




def send(packetString, writeDesc):
	# Send the string of a packet to C handler
	if writeDesc:
		os.write(writeDesc, packetString.encode())
		print("Packet sent : " + packetString)
	else :
		print("[!] Error : Cannot send message. No connection to C handler.")


def receive_string(readDesc, block = True):
    # receive packet string from C handler
	if readDesc:
		if len(packetQueue) > 0 :
			p = packetQueue.pop(0)
			print("je prend ça de la file", p.stringify())
			return p
		else :
			try :
				packetString = ""
				while len(packetString) == 0 or packetString[-1] != "\n" :
					# print("ici : " + packetString)
					packetString += os.read(readDesc, 512).decode()
					if len(packetString) == 0 and not block :
						break
				if len(packetString) > 0 :
					s = packetString.split("\n")
					for p in s :
						packetQueue.append(packetify(p))
						print("Ajout dans la file", p)
					p = packetQueue.pop(0)
					print("je prend ça de la file", p.stringify())
					return p
				else :
					return packetString

			except OSError as e:
				return ""
	else :
		print("[!] Error : Cannot receive message. No connection to C handler.")
		return ""


packetQueue = []
