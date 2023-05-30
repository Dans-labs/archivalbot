# https://ldn-inbox.labs.dans.knaw.nl/

import requests


class LDN_Inbox_Reader:

    def __init__(self, inbox_url):
        self.inbox_url = inbox_url
        # Todo: Do we need authentication mechanism like token or username/password?
        # self.api_token = api_token

    def read(self):
        response = requests.get(self.inbox_url)
        if response.status_code != 200:
            return "URL error"
        return response.content

    def retrieve_subjects(self, graph, a_query):
        results = graph.query(a_query)
        subjects = []
        for result in results.bindings:
            subjects.append(str(result.get('subject')))

        return subjects
