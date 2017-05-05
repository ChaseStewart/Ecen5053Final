import opc
import time

# DEFINES
NUM_PIXELS = 60
ADDRESS = 'localhost:7890'



"""
This script generates a simple and tantalizing pattern to test the LEDs
"""

def rotate(l,n):
	"""
	Helper function
	"""
	# thanks to stackoverflow.com/questions/9457832/python-list-rotation
	return l[n:] + l[:n]


client = opc.Client(ADDRESS)

# connect to the FCServer client, or else spin until connected
if client.can_connect():
	print("connected to %s " % ADDRESS)
else:
	print("Warning: could not connect to %s" % ADDRESS)
	time.sleep(3)

# Red, Blue, and Green 
three_colors = [(255,0,0),(0,255,0),(0,0,255)]


# generate a list of alternating RGBRGB 
intermediate = []
for j in range(NUM_PIXELS):
	intermediate.append(three_colors[j % 3])

my_pixels = []

# now make 3 sets of LEDs rotated by 1 more each
my_pixels.append(intermediate)
my_pixels.append(rotate(intermediate, 1))
my_pixels.append(rotate(intermediate, 2))
i = 0

# forever rotate colors
while True:
	if client.put_pixels(my_pixels[i], channel=0):
		pass
	else:
		print("Not connected!")
	i = (i+1) % 3
	time.sleep(1/2.0)

