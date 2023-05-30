# Use transformer.labs.dans.knaw.nl
import json
import logging

import requests


class MetadataMapper:
    def __init__(self, transformer_url, api_token, xslt_name):
        self.transformer_url = transformer_url
        self.api_token = api_token
        self.xslt_name = xslt_name

    def get_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
        return headers

    def transform(self, json_input):
        transformer_response = requests.post(self.transformer_url, headers=self.headers,
                                             data=json.dumps(json_input))
        if transformer_response.status_code != 200:
            print(f"ERROR status code: {transformer_response.status_code}")
            logging.error(f"Error response from transformer with error code {transformer_response.status_code}")
        else:
            print(transformer_response.content)
            resp_data = transformer_response.json()['result']
            return resp_data
