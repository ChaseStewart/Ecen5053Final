import opc
import time

NUM_PIXELS = 60
ADDRESS = 'localhost:7890'


def rotate(l,n):
	"""
	Rotate an array
	This function thanks to stackoverflow.com/questions/9457832/python-list-rotation
	"""
	return l[n:] + l[:n]



"""
START the program
"""

client = opc.Client(ADDRESS)

if client.can_connect():
	print("connected to %s " % ADDRESS)
else:
	print("Warning: could not connect to %s" % ADDRESS)
	time.sleep(3)

three_colors = [(255,0,0),(0,255,0),(0,0,255)]
intermediate = []

for j in range(NUM_PIXELS):
	intermediate.append(three_colors[j % 3])

my_pixels = []
my_pixels.append(intermediate)
my_pixels.append(rotate(intermediate, 1))
my_pixels.append(rotate(intermediate, 2))
i = 0

# rotate between the three settings within my_pixels
while True:
	if client.put_pixels(my_pixels[i], channel=0):
		pass
	else:
		print("Not connected!")
	i = (i+1) % 3
	time.sleep(1/2.0)

