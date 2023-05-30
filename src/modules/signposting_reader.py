# http://0.0.0.0:1947/links/links-01.json
import requests


class SignpostingReader:

   def read_head(self, url):
       response = requests.head(url)
       if response.status_code != 200:
        # TODO Logging and raise exception here.
        pass
       else:
           return response.headers#Is this correct??
