from twisted.internet import reactor, protocol
from twisted.internet.endpoints   import clientFromString
from twisted.application.internet import ClientService, backoffPolicy

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from mqtt.client.factory import MQTTFactory
import txthings.resource as resource
import txthings.coap     as coap
from time import time

BROKER = "tcp:test.mosquitto.org:1883"

# -------------------
# Stand-in Protocols
# -------------------

class fake_WSProto(protocol.Protocol):
	def dataReceived(self, data):
		print "Would have been Websockets"

class fake_MQTTProto(protocol.Protocol):
	def dataReceived(self,data):
		print "Would have been MQTT"

class fake_CoAPProto(protocol.Protocol):
	def dataReceived(self,data):
		print "Would have been CoAP"


class WSProto(WebSocketServerProtocol):
	"""
	Simple protocol to measure WebSocket overhead
	"""

	def onConnect(self, request):
		pass

	def onOpen(self):
		pass

	def onMessage(self, payload, isBinary):
		"""
		Calculate overhead in size and time
		"""
		now = time()
		delta = now - float(format(payload.decode('utf8')))
		print("packet_len is "+str(len(payload)))
		print ("Delta time is "+str(delta))
		# TODO need


class CoAPProto(resource.CoAPResource):
	def __init__(self, start=0):
		pass



class MQTTProto(ClientService):
	"""
	MQTT protocol
	"""
	def __init(self, endpoint, factory):
	        ClientService.__init__(self, endpoint, factory, retryPolicy=backoffPolicy())

	def startService(self):
		pass

	


def main():
	"""
	Just start all 3 protos
	"""

	# WS listener 
	ws_factory = WebSocketServerFactory(u"ws://localhost:8000")
	ws_factory.protocol = WSProto
	reactor.listenTCP(8000, ws_factory)

	# TODO MQTT listener
	mqtt_factory  = MQTTFactory(profile=MQTTFactory.SUBSCRIBER)
	mqtt_endpoint = clientFromString(reactor, BROKER)
	mqtt_serv     = MQTTService(mqtt_endpoint, mqtt_factory)
	mqtt_serv.startService()

	# TODO CoAP listener
	coap_factory = protocol.ServerFactory()
	coap_factory.protocol = fake_CoAPProto
	reactor.listenTCP(8002, coap_factory)
	
	reactor.run()



if __name__ == "__main__":
	infostr="""
	*** OVERHEAD CALCULATION ***

	Send a standard message to each protocol
	----------------------------------------

	Websockets: port 8000
	MQTT:       port 8001
	CoAP:       port 8002
	"""
	
	print infostr
	main()

