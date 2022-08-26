import RPi.GPIO as GPIO
import signal
import time


def end_run(signal, frame):
    global keep_running
    print("ctrl + c captured, end run")
    global active_led
    GPIO.output(active_led, GPIO.LOW)
    GPIO.cleanup()
    keep_running = False


def blink(gpio, is_high):
    if is_high:
        GPIO.output(gpio, GPIO.HIGH)
    else:
        GPIO.output(gpio, GPIO.LOW)


# ctrl + c => Stop
signal.signal(signal.SIGINT, end_run)
# config GPIO
GPIO.setmode(GPIO.BCM)

# welcome
print("-------FLEXSO FLOW METER-------")
print("")
print("")
print("\trunning...")
print("")
print("\tpress ctrl + c to stop")

# main loop
keep_running = True
active_led = 17
GPIO.setup(active_led, GPIO.OUT)
while keep_running:
    blink(active_led, True)
    time.sleep(1)
    blink(active_led, False)
    time.sleep(1)
