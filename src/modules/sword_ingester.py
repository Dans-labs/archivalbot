# curl -k -u API_KEY: https://dar.dans.knaw.nl/dvn/api/data-deposit/v1.1/swordv2/service-document
import codecs
import os

import requests
from sword2 import Connection


class SwordIngester:
    def __init__(self, sd_iri, username, password):
        self.sd_iri = sd_iri
        self.username = username
        self.password = password
        self.connection = Connection(self.sd_iri, self.username, self.password)

    def create_dataset(self):

        url = f'{self.sd_iri}/dataverse/root'
        file_path = 'atom-dv.xml'
        headers = {'Content-Type': 'application/atom+xml'}

        with open(file_path, 'rb') as file:
            file_content = file.read()
            # response = requests.post(url, auth=(self.username, self.password), data=file_content, headers=headers)
            response = requests.get(url, auth=(self.username, self.password), data=file_content)
            test = response.status_code
            print(test)

        return response.status_code

    def ingest(self, bag_abs_path):
        with codecs.open(bag_abs_path, "r", encoding='utf-8', errors='ignore') as pkg:
            receipt = self.connection.create(col_iri=self.sd_iri,
                               payload=pkg,
                               mimetype="application/zip",
                               filename=os.path.basename(bag_abs_path),
                               packaging='http://purl.org/net/sword/package/Binary',
                               in_progress=True)


    def remove_original_bagit_file(self, bag_abs_path):
        #TODO: Check the ingesting progress. If it is complete, we can remove the origignal bagit file.

        os.remove(bag_abs_path)