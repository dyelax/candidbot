from __future__ import print_function
from time import sleep
from picamera import PiCamera
import os

from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/drive'


class DriveUploader:
  def __init__(self):
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
      flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
      creds = tools.run_flow(flow, store)

    self.drive = discovery.build('drive', 'v3', http=creds.authorize(Http()))


  def upload(self, file_path):
    metadata = {'name': file_path}
    res = self.drive.files().create(body=metadata, media_body=file_path).execute()
    if res:
      print('Uploaded "%s" (%s)' % (file_path, res['mimeType']))




def main():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  uploader = DriveUploader()

  os.chdir("/home/pi/candidbot/images")
  camera = PiCamera()
  camera.start_preview()
  sleep(2)
  counter = 0
  for filename in camera.capture_continuous('{timestamp}.jpg'):
    counter += 1
    print('Captured %s' % filename)
    uploader.upload(filename)
    if counter > 30:
      exit()


if __name__ == '__main__':
  main()
