# https://ldn-inbox.labs.dans.knaw.nl/
import json
import os
import time
from datetime import datetime

import jinja2
import polling2
import requests
from rdflib import Graph
from jsonpath_ng.ext import parse

from src.commons import settings
from src.modules.ldn_inbox_reader import LDN_Inbox_Reader

query_valid_offer_types = """
                PREFIX sorg: <http://schema.org/>
                PREFIX as: <https://www.w3.org/ns/activitystreams#>
                SELECT ?subject
                WHERE {
                  ?subject a sorg:AboutPage, sorg:Dataset, as:Document.
                }
            """

query_offer_id = """
                PREFIX as: <https://www.w3.org/ns/activitystreams#>
                SELECT ?subject
                WHERE {
                  ?subject a as:Offer.
                }
                """

query_obj_id = """
                PREFIX as: <https://www.w3.org/ns/activitystreams#>
                PREFIX sorg: <http://schema.org/>   
                SELECT ?subject
                WHERE {
                  ?subject a sorg:AboutPage.
                }
                """

query_author_id = """
                PREFIX as: <https://www.w3.org/ns/activitystreams#>
                SELECT ?subject
                WHERE {
                  ?subject a as:Person.
                }
                """


class LDN_Inbox_Poller:

    def __init__(self, ldn_inbox_url, interval_time_in_seconds):
        self.ldn_inbox_url = ldn_inbox_url
        self.interval_time_in_seconds = interval_time_in_seconds

    def is_correct_response(self, response):
        """Check that the response returned 'success'"""

        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print(f"Start read inbox at: {current_time}")
        ldn_inbox_reader = LDN_Inbox_Reader(self.ldn_inbox_url)
        i = 0
        cur_working_dir = os.getcwd()
        cur_parent_dir = os.path.abspath(os.path.join(cur_working_dir, os.pardir))
        templateLoader = jinja2.FileSystemLoader(
            searchpath=f'{cur_parent_dir}/{settings.JINJA2_TEMPLATE_PATH}')
        templateEnv = jinja2.Environment(loader=templateLoader)
        jinja_json_template = templateEnv.get_template(settings.JINJA2_TEMPLATE_ACCEPT)
        for payload in json.loads(ldn_inbox_reader.read()):
            i += 1
            graph = Graph().parse(data=json.loads(payload['payload']), format='json-ld')
            graph_result = graph.serialize(format='ttl')

            # TODO: Is validation for all sorg:AboutPage, sorg:Dataset, as:Document? or only for sorg:AboutPage?

            types_offer = ldn_inbox_reader.retrieve_subjects(graph, query_valid_offer_types)
            if len(types_offer) == 0:
                print("TYPES NOT VALID")
                break

            object_id = ldn_inbox_reader.retrieve_subjects(graph, query_obj_id)

            offer_id = ldn_inbox_reader.retrieve_subjects(graph, query_offer_id)

            author_id = ldn_inbox_reader.retrieve_subjects(graph, query_author_id)

            accept_json = jinja_json_template.render(object_id=object_id[0], offer_id=offer_id[0], author_id=author_id[0])

            # TODO: create a class from here
            url = ""
            api_token_target = settings.API_TOKEN_TARGET
            headers = {
                "Content-Type": "application/ld+json",
                "Authorization": "Bearer " + api_token_target
            }

            response = requests.post(url, headers=headers, data=accept_json)


            dummy_url_head = "http://localhost:2907/page/1"  # TODO: THIS comes from LDN inbox
            resp_head = requests.head(dummy_url_head)

            print("Response Headers from DUMMY:")

            for header, value in resp_head.headers.items():
                print(f"{header}: {value}")
                if header == 'location':
                    linkset_location = value
                    break

            resp_linkset = requests.get(linkset_location)

            linkset_t = resp_linkset.text

            jsonpath_exp = parse("$.item[*]")
            items = []
            for match in jsonpath_exp.find(linkset_t):
                print(match.value)
                items.append(match.value)

            time.sleep(5)

        current_time2 = now.strftime("%H:%M:%S")
        print(f"END read inbox at: {current_time2}")
        print()
        print("READY for the next polling..")

        return response == 'success'

    def run(self):
        polling2.poll(target=lambda: self.is_correct_response(self), step=self.interval_time_in_seconds,
                      poll_forever=True)
