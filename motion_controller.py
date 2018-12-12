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
    self.init_wheels()
    # Make the wheels turn the bot a little bit left
    # self.stop()

    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, True)
    # time.sleep(0.2)
    time.sleep(2)

    # self.stop()
    gpio.cleanup()


  def turn_right(self):
    self.init_wheels()
    # Make the wheels turn the bot a little bit right
    # self.stop()

    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, True)
    gpio.output(24, False)
    # time.sleep(0.2)
    time.sleep(2)

    # self.stop()
    gpio.cleanup()


  def turn_90(self):
    self.init_wheels()
    # Turn left 90 degrees
    # self.stop()

    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, True)
    # time.sleep(2)
    time.sleep(10)

    # self.stop()
    gpio.cleanup()


  def stop(self):
    self.init_wheels()
    gpio.output(17, False)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, False)
    time.sleep(0.2)
    gpio.cleanup()


  def go_forward(self):
    self.init_wheels()
    # Make the wheels move the bot a little bit forward
    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, True)
    gpio.output(24, False)
    gpio.cleanup()


  def go_backward(self):
    self.init_wheels()
    # Make the wheels move the bot a little bit backward
    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, False)
    gpio.output(24, True)
    gpio.cleanup()


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

