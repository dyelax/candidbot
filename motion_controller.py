import RPi.GPIO as gpio
import time


class MotionController:
  def __init__(self):
    self.init_wheels()
    self.stop()

  def init_wheels(self):
    gpio.setmode(gpio.BCM)
    gpio.setup(17, gpio.OUT)
    gpio.setup(22, gpio.OUT)
    gpio.setup(23, gpio.OUT)
    gpio.setup(24, gpio.OUT)

  def turn_left(self):
    # Make the wheels turn the bot a little bit left
    self.stop()

    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, True)
    time.sleep(0.2)

    self.stop()
    time.sleep(0.3)

  def turn_right(self):
    # Make the wheels turn the bot a little bit right
    self.stop()

    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, True)
    gpio.output(24, False)
    time.sleep(0.2)

    self.stop()
    time.sleep(0.3)

  def turn_90(self):
    # Turn left 90 degrees
    self.stop()

    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, True)
    time.sleep(1)

    self.stop()
    time.sleep(0.3)

  def stop(self):
    gpio.output(17, False)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, False)
    time.sleep(4)

  def go_forward(self):
    # Make the wheels move the bot a little bit forward
    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, True)
    gpio.output(24, False)
    time.sleep(1)

    self.stop()

  def go_backward(self):
    # Make the wheels move the bot a little bit backward
    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, False)
    gpio.output(24, True)

    time.sleep(1)

  def close(self):
    self.stop()
    gpio.cleanup()
