var http = require('http');
var deviceModule = require('/home/centos/node_modules/aws-iot-device-sdk').device;

// This node.js program listens for a AJAX call from the website with RGB values for the LED
// when it gets a message, it publishes to the AWS IOT framework



var common = '/home/centos/'

function publishRGB(Red,Green,Blue){
	// setup AWS
   	clientIdDefault = 'nouser' + (Math.floor((Math.random() * 100000) + 1));

	const device = deviceModule({
	   keyPath: common+'Web01.private.key',
	   certPath: common+'Web01.cert.pem',
	   caPath: common+'root-CA.crt',
	   clientId: clientIdDefault,
	   region: 'us-west-2',
	   baseReconnectTimeMs: 4000,
	   keepalive: 30,
	   protocol: 'mqtts',
	   port: 8883,
	   host: 'a1qhmcyp5eh8yq.iot.us-west-2.amazonaws.com',
	   debug: false
	});

	// Publish the LED values to AccessControl/set_leds
	device.publish('AccessControl/set_leds', JSON.stringify({"type":"led","red":Red, "green":Green, "blue":Blue	}));

	//
	// Do a simple publish/subscribe demo based on the test-mode passed
	// in the command line arguments.  If test-mode is 1, subscribe to
	// 'topic_1' and publish to 'topic_2'; otherwise vice versa.  Publish
	// a message every four seconds.
	//
	device
	.on('connect', function() {
		console.log('connect');
	});
	device
	.on('close', function() {
		console.log('close');
	});
	device
	.on('reconnect', function() {
		console.log('reconnect');
	});
	device
	.on('offline', function() {
		console.log('offline');
	});
	device
	.on('error', function(error) {
		console.log('error', error);
	});
	device
	.on('message', function(topic, payload) {
		console.log('message', topic, payload.toString());
	});
}

// create the listener
http.createServer(function (request, response) {
	// allow cross- origin requests
	response.writeHead(200, {
	    'Content-Type': 'text/plain',
	    'Access-Control-Allow-Origin' : '*',
	});

	var body = '';
	// get data one chunk at a time
	request.on('data', function(chunk){
		body += chunk;
	
	});
	// once all data is received, publish it
	request.on('end', function(data){
		var my_json = JSON.parse(body)
		var red   = my_json['r'];
		var green = my_json['g'];
		var blue  = my_json['b'];
		LED_string = 'Red: '+red+' Green: '+green+' Blue: '+blue+' \n';
		console.log(LED_string);
		publishRGB(red, green, blue);
	});
	// send back a stupid response
	response.end("THANKS FOR THE INFO");
}).listen(8080);

// print a lil message
console.log('Listening on port 8080')
