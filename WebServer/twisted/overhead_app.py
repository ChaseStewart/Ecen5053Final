from twisted.internet import reactor, protocol
from twisted.internet.defer       import inlineCallbacks, DeferredList
from twisted.internet.endpoints   import clientFromString
from twisted.application.internet import ClientService, backoffPolicy

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from mqtt.client.factory import MQTTFactory
import txthings.resource as resource
import txthings.coap     as coap
from time import time
import sys, json

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# globals 
BROKER = "tcp:test.mosquitto.org:1883"
mqtt_latency = None
mqtt_size    = None
coap_latency = None
coap_size    = None
ws_latency   = None
ws_size      = None


rootCA      = "root-CA.crt"
privatePath = "sim_access.private.key"
certPath    = "sim_access.cert.pem"
myhost        = "alqhmcyp5eh8yq.iot.us-west-2.amazonaws.com"
myhost="a1qhmcyp5eh8yq.iot.us-west-2.amazonaws.com" 



class PerfPublisher():
	def __init__(self):
		self.mqtt_latency = None 
		self.mqtt_size    = None
		self.has_mqtt     = False

		self.coap_latency = None
		self.coap_size    = None
		self.has_coap     = False

		self.ws_latency   = None
		self.ws_size      = None
		self.has_ws       = False

	def clearVals(self):
		self.mqtt_latency = None
		self.mqtt_size    = None
		self.has_mqtt     = False
		
		self.coap_latency = None
		self.coap_size    = None
		self.has_coap     = False
		
		self.ws_latency   = None
		self.ws_size      = None
		self.has_ws       = False

	def setVals(self, protocol, latency, size):
		if protocol == "MQTT" and self.mqtt_latency == None and self.mqtt_size == None:
			self.mqtt_latency = latency
			self.mqtt_size    = size
			self.has_mqtt     = True

		elif protocol == "CoAP" and self.coap_latency == None and self.coap_size == None:
			self.coap_latency = latency
			self.coap_size    = size
			self.has_coap     = True

		elif protocol == "WS" and self.ws_latency == None and self.ws_size == None:
			self.ws_latency = latency
			self.ws_size    = size
			self.has_ws     = True	
		
		print ("WS: %s, CoAP: %s, MQTT: %s" % (self.has_ws, self.has_coap, self.has_mqtt))
		if self.has_ws and self.has_coap and self.has_mqtt:
			self.publishJSON()	


	def publishJSON(self):
		AWSClient = AWSIoTMQTTClient("basicPubSub")
		AWSClient.configureEndpoint(myhost, 8883)
		AWSClient.configureCredentials(rootCA, privatePath, certPath)

		AWSClient.configureAutoReconnectBackoffTime(1,32,20)
		AWSClient.configureOfflinePublishQueueing(-1)
		AWSClient.configureDrainingFrequency(2)
		AWSClient.configureConnectDisconnectTimeout(10)
		AWSClient.configureMQTTOperationTimeout(10)
		AWSClient.connect()

		jsonData = {}	
		jsonData['type'] = 'overhead'
		jsonData['mqtt_lat'] = self.mqtt_latency
		jsonData['mqtt_ovh'] = self.mqtt_size
		jsonData['ws_lat']   = self.ws_latency
		jsonData['ws_ovh']   = self.ws_size
		jsonData['coap_lat'] = self.coap_latency
		jsonData['coap_ovh'] = self.coap_size

		strData= json.dumps(jsonData)
		print("Published data!")
		#print strData
		AWSClient.publish("AccessControl/performance", str(strData), 1)
		self.clearVals()


# Fake protos

class fake_WSProto(protocol.Protocol):
	def dataReceived(self, data):
		print "Would have been Websockets"

class fake_MQTTProto(protocol.Protocol):
	def dataReceived(self,data):
		print "Would have been MQTT"

class fake_CoAPProto(protocol.Protocol):
	def dataReceived(self,data):
		print "Would have been CoAP"



# real protos

class WSProto(WebSocketServerProtocol):
	"""
	Simple protocol to measure WebSocket overhead
	"""

	def onConnect(self, request):
		"Websockets connected localhost:8000\n"
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

		ws_latency   = delta
		ws_size      = len(payload)
		print("Took websockets measurement")
		global publisher
		publisher.setVals("WS", ws_latency, ws_size)


class CoAPProto(resource.CoAPResource):
	"""
	CoAP Protocol
	"""
	#isLeaf = True

	def __init__(self, start=0):
		resource.CoAPResource.__init__(self)
		self.visible=True
		self.addParam(resource.LinkParam("title", "delta resource"))
		print("CoAP connected to localhost:5683\n")

	def render_GET(self, request):
		payload = "Use GET instead!"
		response = coap.Message(code=coap.CONTENT, payload = payload)
		return defer.succeed(response)

	def render_PUT(self, request):
		now = time()
		delta = now - float(request.payload)
		print request.payload
		print("packet_len is "+str(len(request.payload)))
		print ("Delta time is "+str(delta))
		coap_latency   = delta
		coap_size      = len(request.payload)
		global publisher
		print("Took CoAP measurement")
		publisher.setVals("CoAP", coap_latency, coap_size)
		response = coap.Message(code=coap.CHANGED, payload=str(delta))
		return deferred 



class MQTTProto(ClientService):
	"""
	MQTT protocol
	"""
	def __init(self, endpoint, factory):
	        ClientService.__init__(self, endpoint, factory, retryPolicy=backoffPolicy())

	def startService(self):
		print("starting MQTT Client Subscriber Service")
		# invoke whenConnected() inherited method
		self.whenConnected().addCallback(self.connectToBroker)
		ClientService.startService(self)


	@inlineCallbacks
	def connectToBroker(self, protocol):
		'''
		Connect to MQTT broker
		'''
		self.protocol                 = protocol
		self.protocol.onPublish       = self.onPublish
		self.protocol.onDisconnection = self.onDisconnection
		self.protocol.setWindowSize(3)
		try:
			yield self.protocol.connect("TwistedMQTT-subs", keepalive=60)
			yield self.subscribe()
		except Exception as e:
			print("Connecting to %s raised exception %s\n" % (BROKER, e) )
			sys.exit()
		else:
			print("Connected and subscribed to %s\n" % BROKER)


	def subscribe(self):
		def _print_result():
			print("Connected!")
		
		def _print_done(self):
			print("Done")

		d1 = self.protocol.subscribe("AccessControl/MQTT_test", 2)
		d1.addCallbacks(_print_result)

		dlist = DeferredList([d1], consumeErrors=True)
		dlist.addCallback(_print_done)
		return dlist


	def onPublish(self, topic, payload, qos, dup, retain, msgId):
		'''
		Callback Receiving messages from publisher
		'''
		now = time()
		delta = now - float(format(payload.decode('utf8')))
		print("packet_len is "+str(len(payload)))
		print ("Delta time is "+str(delta))
		
		mqtt_latency   = delta
		mqtt_size      = len(payload)
		print("Took MQTT measurement")

		global publisher
		publisher.setVals("MQTT", mqtt_latency, mqtt_size)

	def onDisconnection(self, reason):
		'''
		get notfied of disconnections
		and get a deferred for a new protocol object (next retry)
		'''
		print(" >< Connection was lost ! ><, reason={%s}" % reason)
		self.whenConnected().addCallback(self.connectToBroker)

	
def printResult(result):
	print(result)

def printError(failure):
	import sys
	sys.stderr.write(str(failure))

def main():
	"""
	Just start all 3 protos
	"""

	# WS listener 
	ws_factory = WebSocketServerFactory(u"ws://52.34.209.113:8000")
	ws_factory.protocol = WSProto
	reactor.listenTCP(8000, ws_factory)

	# MQTT listener
	mqtt_factory  = MQTTFactory(profile=MQTTFactory.SUBSCRIBER)
	mqtt_endpoint = clientFromString(reactor, BROKER)
	mqtt_serv     = MQTTProto(mqtt_endpoint, mqtt_factory)
	mqtt_serv.startService()

	# CoAP listener
	coap_root = resource.CoAPResource()
	coap_ovh  = CoAPProto()
	coap_root.putChild('test',coap_ovh)
	coap_endpoint = resource.Endpoint(coap_root)
	reactor.listenUDP(coap.COAP_PORT, coap.Coap(coap_endpoint))
	
	# run the program
	reactor.run()



if __name__ == "__main__":
	infostr="""
	*** OVERHEAD CALCULATION ***

	Send a standard message to each protocol
	----------------------------------------

	Websockets:	host: localhost
			port: 8000

	MQTT:		host:	test.mosquitto.org
			port:	1883 
			topic:	MQTT_test

	CoAP:		host:	localhost
			port:	5683
			topic:	test

	----------------------------------------
	
	Results are published to AWS IOT

	topic:	AccessControl/performance
	form:	{'byte':<overhead_in_bytes>, 'time':<delta_time>}

	"""
	
	# create publisher
	publisher = PerfPublisher()
	print infostr

	# run main function
	main()

