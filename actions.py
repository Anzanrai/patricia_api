# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

import rasa_sdk
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Hello World!")

        return []


class GetHeritageTitle(Action):

    def name(self) -> Text:
        return "get_heritage_title"

    def run(self, dispatcher, tracker, domain):
        res = requests.get("http://localhost:8000/events-api/heritage")
        # print(res.json())
        heritages = res.json()
        heritage_name = [heritage['name'] for heritage in heritages]
        response = "Heritage of Parramatta City Council:\n{}".format(heritage_name)
        dispatcher.utter_message(response)


class GetHeritageDetail(Action):

    def name(self) -> Text:
        return "get_heritage_detail"

    def run(self, dispatcher, tracker, domain):
        heritage_name = tracker.get_slot('heritage_name')
        print("**********************", heritage_name, "****************")
        base_url = "http://localhost:8000/events-api/heritage/"
        if heritage_name:
            url = base_url + "?name="+heritage_name
        else:
            url = base_url
        print(url)
        res = requests.get(url)
        if res.status_code == 200:
            print("Successful response!!!")
            heritage_detail = res.json()
            if len(heritage_detail) >= 1:
                heritage_detail_description = heritage_detail[0]
                utter_message = heritage_detail_description.get('description')
                if heritage_detail_description.get('open_time', ''):
                    utter_message += "\n\n{} can be visited between the time {} and {} on {}".\
                        format(heritage_name, heritage_detail_description.get('open_time'),
                               heritage_detail_description.get('close_time'), heritage_detail_description.get('open_days'))
                dispatcher.utter_message(utter_message)
                return [SlotSet("heritage_name", heritage_name)]
            else:
                if heritage_name:
                    url = "http://localhost:8000/events-api/suggestive_heritage/?heritage_name="+heritage_name
                else:
                    url = "http://localhost:8000/events-api/suggestive_heritage/"
                print("query url: ", url)
                res = requests.get(url)
                if res.status_code == 200:
                    print("Successful response!!!")
                    heritage_detail = res.json()
                    if len(heritage_detail) >= 1:
                        suggestive_heritage_name = heritage_detail[0].get('name')
                    error_message = "It seems I could not find detail on "+heritage_name+\
                                    ". Did you mean "+suggestive_heritage_name+"?"
                dispatcher.utter_message(error_message)
                return [rasa_sdk.events.FollowupAction('get_contact_person'), SlotSet('designation', 'customer support')]
        else:
            print("Error in retrieving response")
            error_message = "Sorry, but I am having trouble fetching data from server."


class GetContactPerson(Action):
    def name(self) -> Text:
        return "get_contact_person"

    def run(self, dispatcher, tracker, domain):
        designation = tracker.get_slot('designation')
        print('*************',designation,'****************')
        base_url = 'https://localhost:8000/api/contact-person/'
        if designation:
            url = base_url+'?designation='+designation
        else:
            url = base_url+'?designation=customer support'
        res = requests.get(url)
        if res.status_code == 200:
            print('Response obtained successfully.')
            contact_person = res.json()
            if len(contact_person) >= 1:
                contact_person_detail = contact_person[0]
                utter_message = "You can contact "+contact_person_detail.get('get_full_name')+" at the email address "\
                          + contact_person_detail.get('email') + " or you can call in the number " + \
                          contact_person_detail.get('mobile_number')
                dispatcher.utter_message(utter_message)
                return [SlotSet("designation", designation)]
        else:
            print("Error in retrieving response")
            error_message = "Sorry, but I am having trouble fetching data from server."

# class ActionQueryLibraryMembership(Action):
#     def name(self) -> Text:
#         return "action_library_membership"
#
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         response = "To join our library, you can visit one of our branch libraries or you can register online via " \
#                    "the link https://libreg.cityofparramatta.nsw.gov.au/ Fill up the form and register. A temporary " \
#                    "library card number is provided. You have to visit one of our library branches with the number " \
#                    "and an identification document. A library card will be issued and you will be able to start " \
#                    "borrowing items. Parents or guardians of children or teens under 18 will need to provide their " \
#                    "own identification, along with documents (i.e. Medicare card) showing their relationship. If you " \
#                    "do not show ID within 6 weeks, the temporary card will be deleted."
#         dispatcher.utter_message(response)
#
#         return []