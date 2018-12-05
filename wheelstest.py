import RPi.GPIO as gpio
import time


def init():
    gpio.setmode(gpio.BCM)
    gpio.setup(17, gpio.OUT)
    gpio.setup(22, gpio.OUT)
    gpio.setup(23, gpio.OUT)
    gpio.setup(24, gpio.OUT)

def turn_left():
  # TODO: Make the wheels turn the bot a little bit left
    init()
    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, True)
    time.sleep(.2)
    gpio.cleanup()


def turn_right():
  # TODO: Make the wheels turn the bot a little bit right
    init()
    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, True)
    gpio.output(24, False)
    time.sleep(.2)
    gpio.cleanup()

def turn_90():
  # TODO: Turn left 90 degrees
    init()
    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, True)
    time.sleep(2)
    gpio.cleanup()

def go_forward():
  # TODO: Make the wheels move the bot a little bit forward
    init()
    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, True)
    gpio.output(24, False)
    time.sleep(1)
    gpio.cleanup()


def go_backward():
    # TODO: Make the wheels move the bot a little bit backward
    init()
    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, False)
    gpio.output(24, True)
    time.sleep(1)
    gpio.cleanup()


PROXIMITY_THRESH = 100  # TODO: play with this number
def proximity_warning():
  # TODO: Return whether the distance from the proximity sensor is closer than PROXIMITY_THRESH
  pass

go_forward()
time.sleep(2)
turn_right()
turn_right()
turn_right()
time.sleep(2)
turn_left()
time.sleep(2)
go_backward()
time.sleep(2)
turn_90()
