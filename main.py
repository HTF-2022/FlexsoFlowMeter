#!/usr/bin/python
import RPi.GPIO as GPIO
import signal
import time
import datetime
import paho.mqtt.client as paho
from paho import mqtt
import json

def end_run(signal, frame):
    global keep_running
    GPIO.cleanup()
    client.loop_stop()
    print("run stopped")
    print("BYE")
    keep_running = False

def countPulse(channel):
    global count
    if start_counter == 1:
        count = count + 1

# MQTT
hostname = "ac24c670632142bab0a422606038f608.s1.eu.hivemq.cloud"
port = 8883

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

# enable TLS for secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client.username_pw_set("flexso", "flexsohtf")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect(hostname, port)

# setting callbacks, use separate functions like above for better visibility
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

# loop_forever for simplicity, here you need to stop the loop manually
# you can also use loop_start and loop_stop
client.loop_start()
# ctrl + c => Stop
signal.signal(signal.SIGINT, end_run)

# welcome
print("-------FLEXSO FLOW METER-------")
print("")
print("")
print("\trunning...")
print("")
print("\tpress ctrl + c to stop")

# config GPIO
GPIO.setmode(GPIO.BCM)
FLOW_SENSOR_PIN = 13
GPIO.setup(FLOW_SENSOR_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP )
GPIO.add_event_detect(FLOW_SENSOR_PIN, GPIO.FALLING, callback=countPulse)
global count
count = 0

# main loop
keep_running = True

while keep_running:
    try:
        start_counter = 1
        time.sleep(1)
        start_counter = 0
        flow = (count / 7.5)# Pulse freq (Hz) = 7.5Q, Q is flow rate in L/min
        dtime = datetime.datetime.now()
        message = {"flow": flow, "datetime": dtime.strftime("%Y-%m-%d %H:%M:%S"), "descr": "flow rate in L/min"}
        msg_json = json.dumps(message)
        print(msg_json)
        # publish flow here
        client.publish("/flowMeter", payload=msg_json, qos=1)
        count = 0
        time.sleep(1)
    except KeyboardInterrupt:
        end_run()
