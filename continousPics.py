from time import sleep
from picamera import PiCamera
import os

os.chdir("/home/pi/candidbot/images")

camera = PiCamera()
camera.start_preview()
sleep(2)
for filename in camera.capture_continuous('{timestamp}.jpg'):
  print('Captured %s' % filename)
  sleep(1)
