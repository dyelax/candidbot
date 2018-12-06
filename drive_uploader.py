from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/drive'


# import asyncio
# from aiogoogle import Aiogoogle



class DriveUploader:
  def __init__(self):
    store = file.Storage('storage.json')
    self.creds = store.get()
    if not self.creds or self.creds.invalid:
      flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
      self.creds = tools.run_flow(flow, store)

    self.drive = discovery.build('drive', 'v3', http=self.creds.authorize(Http()))

    self.async_creds = {
      'access_token': self.creds.access_token,
      'expires_at': self.creds.token_expiry,
    }

  # def upload_async(self, file_path):
  #   async def get_res():
  #     async with Aiogoogle(user_creds=self.async_creds) as aiogoogle:
  #       drive_v3 = await aiogoogle.discover('drive', 'v3')
  #       res = await aiogoogle.as_user(drive_v3.files.create(upload_file=file_path))
  #       if res:
  #         print('Uploaded "%s" (%s)' % (file_path, res['mimeType']))
  #
  #   asyncio.run(get_res())

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
  # uploader.upload('test/test1.jpg')
  uploader.upload_async('test/test1.jpg')
  print('Done')


if __name__ == '__main__':
  main()
