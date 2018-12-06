import RPi.GPIO as gpio
import time


def init():
  gpio.setmode(gpio.BCM)
  gpio.setup(17, gpio.OUT)
  gpio.setup(22, gpio.OUT)
  gpio.setup(23, gpio.OUT)
  gpio.setup(24, gpio.OUT)


def turn_left():
  # Make the wheels turn the bot a little bit left
  init()
  gpio.output(17, True)
  gpio.output(22, False)
  gpio.output(23, False)
  gpio.output(24, True)
  time.sleep(.2)
  gpio.cleanup()


def turn_right():
  # Make the wheels turn the bot a little bit right
  init()
  gpio.output(17, False)
  gpio.output(22, True)
  gpio.output(23, True)
  gpio.output(24, False)
  time.sleep(.2)
  gpio.cleanup()


def turn_90():
  # Turn left 90 degrees
  init()
  gpio.output(17, True)
  gpio.output(22, False)
  gpio.output(23, False)
  gpio.output(24, True)
  time.sleep(2)
  gpio.cleanup()


def go_forward():
  # Make the wheels move the bot a little bit forward
  init()
  gpio.output(17, True)
  gpio.output(22, False)
  gpio.output(23, True)
  gpio.output(24, False)
  time.sleep(1)
  gpio.cleanup()


def go_backward():
  # Make the wheels move the bot a little bit backward
  init()
  gpio.output(17, False)
  gpio.output(22, True)
  gpio.output(23, False)
  gpio.output(24, True)
  time.sleep(1)
  gpio.cleanup()


PROXIMITY_THRESH = 100  # TODO: play with this number
def proximity_warning_center():
  # TODO: Return whether the distance from the center proximity sensor is closer than PROXIMITY_THRESH
  pass

def proximity_warning_left():
  # TODO: Return whether the distance from the left proximity sensor is closer than PROXIMITY_THRESH
  pass

def proximity_warning_right():
  # TODO: Return whether the distance from the right proximity sensor is closer than PROXIMITY_THRESH
  pass
