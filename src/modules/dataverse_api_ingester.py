import json
import logging
import requests


class DataverseIngester:

    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.api_token = api_token

    def get_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'X-Dataverse-key': self.api_token
        }
        return headers

    def get_dataset_id(self, pid):
        response = requests.get(f'{self.base_url}/api/datasets/:persistentId/versions/:draft?persistentId={pid}')
        if response.status_code == 200:
            return response.json()["id"]
        else:
            logging.ERROR(f"{pid} nod found. Error message from {self.base_url} is {response.status_code}")
            #TODO: raise exception here
            return 0

    def delete_dataset(self, id):
        response = requests.delete(f'{self.base_url}/api/datasets/{id}/versions/:draft?key={self.api_token}')
        if response.status_code == 200:
            return True
        else:
            #TODO Logging and raise exception here.
            return False

    def publish_dataset(self, pid):
        response = requests.post(
            f'{self.base_url}/api/datasets/:persistentId/actions/:publish?persistentId={pid}&type=major',
            headers=self.get_headers(),
        )
        if response.status_code == 200:
            return True
        else:
            # TODO Logging and raise exception here.
            return False
    def ingest(self, dv_target, dv_json, files):
        payload = json.loads(dv_json)
        pid = payload['datasetVersion']['protocol'] + ":" + payload['datasetVersion']['authority'] + "/" + payload['datasetVersion']['identifier']
        #Ingest metadata as draft
        dv_import_url = f"{self.base_url}/api/dataverses/{dv_target}/root/datasets/:import?pid={pid}&release=no"
        response = requests.post(dv_import_url,data=payload, headers=self.get_headers())
        dv_release_status = True
        if response.status_code == 201:
            #If success, add files.
            dv_add_files_url = f"{self.base_url}/api/datasets/:persistentId/add?persistentId={pid}"
            for f in files:
                file = {
                    'file': open(f, 'rb')
                }
                response = requests.post(
                    dv_add_files_url,
                    headers=self.get_headers(),
                    files=file,
                )
                if response.status_code != 200:
                    logging.ERROR(f"Return code {response.status_code} for file {f}.")
                    #delete datasets
                    dv_release_status = False
                    ds_id = self.get_dataset_id(pid)
                    self.delete_dataset(ds_id)
                    break;

            # When dv_release_status is true, update release status; otherwise delete the dataset
            if dv_release_status:
                #Publish dataset
                self.publish_dataset(pid)