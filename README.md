# Hubby.io 
This repository holds Chase E Stewart and Mounika Reddy's Super project for CU Boulder ECEN5053 Embedded Interface design, created in Spring semester 2017. 

## What is it?
Hubby.io is the final semester project for Chase E Stewart and Mounika Reddy.

This project implements a Hub device, an Access-Control device, and a webserver. Using these 3 instances and an extensive AWS infrastructure, the project provides the following functions:
* Access Control
* Hub GUI
* Access GUI
* Voice Control
* AWS Infrastructure

## Access Control

#### Login interface
Users can only login to the Access control device, and can do so either via username and password or fingerprint.
Users can add username and password via the public webpage, and can then add or remove a fingerprint ID after authenticating via username and password.

#### Access Fundamentals
The Hub GUI and Access GUI each respond to an "Arm State" provided by messages in an AWS SQS queue that take the form of either
`{"username": "Mounika", "arm_state": "Disarmed", "access": "3", "type": "login"}`
or 
`{"username": "None", "arm_state": "Armed", "access": "0", "type": "login"}`
On receipt of an arm_state="Disarmed" message, the Hub GUI will allow all the functions mentioned below and the Access GUI will allow for adding or removing fingerprints for users. When the logout button is pressed on either device, it immediately publishes this message: 
`{"username": "None", "arm_state": "Armed", "access": "0", "type": "login"}`
Which causes all devices to go to their locked state.

#### Additional Notes
The security of this project is not bulletproof, but much of the infrastructure that would be needed for a good access control system is there. Anyone can make an account using the webpage and I can think of a few ways to subvert/pose as other users, but we just didn't have the time to make a bulletproof access control.

## Hub GUI
The Hub provides the following functions:
* Set LED values (set R, G, B to values between 0 and 255)
* View Stats (moving chart of IoT protocol latency, whether the LED strip is ON or OFF, and RGB by values)
* Logout (publish an "State == Armed" message and go back to the lock screen with 0 functionality)
* Voice Control mode (switch to accepting Voice Commands)

## Access GUI
At first, the Access page gives a prompt for login using either fingerprint (if previously configured for the user) or username and password (always works for a user). All users default to having fingerprints disabled (duhh), and only can enable this by creating a user/password, logging in, then adding fingerprint for themselves.
Access GUI will allow for adding or removing fingerprints for users. When the logout button is pressed on either device, it immediately publishes this message: 


## Voice Control
The Voice API is enabled by clicking the Voice Mode button- Upon clicking the voice button, all hub buttons are hidden and Voice mode commences. The voice API responds to the following commands:
* "lights red"   - set lights to fully red
* "lights blue"  - set lights to fully blue
* "lights green" - set lights to fully green
* "music"        - play the first song from the list
* "next"         - play the next song from the list
* "previous"     - play the previous song from the list
* "stop"         - stop all music
* "who am I "    - say "Hello, < logged in user >" 
* "end voice"    - stop Voice Control mode

## AWS infrastructure
This whole project is built off of the AWS IOT framework, which is an MQTT publish-subscribe protocol that we use for all state information and changes.

The total number of AWS devices we used were:
* 1x RDS
* 3x AWS IoT devices
* 1x CentOS7 EC2 server
* 8x AWS IoT Rules
* 4x Lambda Functions
* 2x SQS Queues

The different types of messages we use are:
* LED setting messages
* Arm state/ user login
* Remove Fingerprint Index
* Add Fingerprint Index
* Username/ Password Entry

#### SQS QUEUES
There are 2 SQS queues, Hub_Messages and Access_Messages
The GUIs read from the queues and process/ acknowledge messages. 

#### RDS
The RDS is our backend server that holds username/password-hash combinations, mappings of fingerprint-id to user, history of adding/removing users, and history of access control states. 

#### EC2
The CentOS server hosts the website, a Node.JS listener for publishing LED messages from the website, and a python Twisted server to measure the latency of various IOT protocols (MQTT, CoAP, and Websockets) for display by the Hub GUI.

#### AWS IoT (Devices, Rules, Lambda Functions)
The IOT rules subscribe to the various message types and execute lambda functions on them (verify username/password against the DB, write/remove fingerprint-to-user entries from the DB, republish ArmState/login messages on successful DB authentication).

## ToDo
We can't promise this will ever get done, as this is a class project, but it would be cool
to create ansible scripts that can deploy the Access, Hub, and Webserver.

This would require far more parameterization of values than currently exists, but it is definitely possible
