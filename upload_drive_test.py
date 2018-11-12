from __future__ import print_function
import os

from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

FILES = ['img004.jpg','img010.jpg']

for filename in FILES:

    metadata = {'name': filename}
    res = DRIVE.files().create(body=metadata, media_body=filename).execute()
    if res:
        print('Uploaded "%s" (%s)' % (filename, res['mimeType']))
