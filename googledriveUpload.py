from __future__ import print_function
from time import sleep
from picamera import PiCamera
import os
os.chdir ("/home/pi/candidbot/images")

from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/drive'

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store, flags='--noauth_local_webserver')
    DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

    camera = PiCamera()
    camera.start_preview()
    sleep(2)

    for filename in camera.capture_continuous('{timestamp}.jpg'):
        print('Captured %s' % filename)
        sleep(1)  # wait 5 minutes
        metadata = {'name': filename}
        res = DRIVE.files().create(body=metadata, media_body=filename).execute()
        if res:
            print('Uploaded "%s" (%s)' % (filename, res['mimeType']))

if __name__ == '__main__':
    main()


