#!/usr/bin/python
import RPi.GPIO as GPIO
import signal
import time
import datetime
import paho.mqtt.publish as publish
import json

def end_run(signal, frame):
    global keep_running
    GPIO.cleanup()
    print("run stopped")
    print("BYE")
    keep_running = False

def countPulse(channel):
    global count
    if start_counter == 1:
        count = count + 1

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

# MQTT
hostname = "ac24c670632142bab0a422606038f608.s1.eu.hivemq.cloud"
port = 8883

# main loop
keep_running = True
while keep_running:
    try:
        start_counter = 1
        time.sleep(1)
        start_counter = 0
        flow = (count / 7.5)# Pulse freq (Hz) = 7.5Q, Q is flow rate in L/min
        datetime = datetime.datetime.now()
        message = {"flow": flow, "datetime": datetime.strftime("%Y-%m-%d %H:%M:%S"), "descr": "flow rate in L/min"}
        msg_json = json.dumps(message)
        print(msg_json)
        # publish flow here
        publish.single("/flowMeter", msg_json, hostname=hostname, retain=True, port=port)
        count = 0
        time.sleep(5)
    except KeyboardInterrupt:
        end_run()
