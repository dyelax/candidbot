import RPi.GPIO as gpio
import time


class MotionController:
  def __init__(self):
    gpio.setmode(gpio.BCM)
    gpio.setup(17, gpio.OUT)
    gpio.setup(22, gpio.OUT)
    gpio.setup(23, gpio.OUT)
    gpio.setup(24, gpio.OUT)

    self.PROXIMITY_THRESH = 100  # TODO: play with this number

  def turn_left(self):
    # Make the wheels turn the bot a little bit left
    self.stop()
    time.sleep(0.2)

    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, True)

    time.sleep(0.2)
    self.stop()

  def turn_right(self):
    # Make the wheels turn the bot a little bit right
    self.stop()
    time.sleep(0.2)

    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, True)
    gpio.output(24, False)

    time.sleep(0.2)
    self.stop()

  def turn_90(self):
    # Turn left 90 degrees
    self.stop()
    time.sleep(0.2)

    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, True)

    time.sleep(2)
    self.stop()

  def stop(self):
    gpio.output(17, False)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, False)

  def go_forward(self):
    # Make the wheels move the bot a little bit forward
    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, True)
    gpio.output(24, False)

  def go_backward(self):
    # Make the wheels move the bot a little bit backward
    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, False)
    gpio.output(24, True)

  def close(self):
    self.stop()
    gpio.cleanup()


  def proximity_warning_center(self):
    # TODO: Return whether the distance from the center proximity sensor is closer than PROXIMITY_THRESH
    pass

  def proximity_warning_left(self):
    # TODO: Return whether the distance from the left proximity sensor is closer than PROXIMITY_THRESH
    pass

  def proximity_warning_right(self):
    # TODO: Return whether the distance from the right proximity sensor is closer than PROXIMITY_THRESH
    pass

