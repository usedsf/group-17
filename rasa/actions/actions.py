import re
import sqlite3
from typing import Any, Text, Dict, List

from actions import Apis
from rasa_sdk import Action, Tracker
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher


class ActionPhone(Action):

    def name(self) -> Text:
        return "phone_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["phone_number", "email"]

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        phone = tracker.get_slot('phone_number')
        email = tracker.get_slot('email')
        pattern = re.compile(r'(((\+86)|(86))?(1)\d{10})|([1-9][0-9]{10}|((\d{3,4}-)?\d{7,8}))')
        p = pattern.match(phone)
        if p is None:
            dispatcher.utter_message(text="Please enter a valid phone number")
            return [UserUtteranceReverted()]
        else:
            conn = sqlite3.connect("customer.db")
            cursor = conn.cursor()
            query1 = "CREATE TABLE IF NOT EXISTS connect (id integer PRIMARY KEY,email text NOT NULL, phone integer NOT NULL);"
            cursor.execute(query1)
            query3 = "SELECT email FROM connect WHERE email = ?"
            e = email,
            cursor.execute(query3, e)
            if not cursor.fetchall():
                query2 = "INSERT INTO connect(email, phone) VALUES(?, ?)"
                cursor.execute(query2, (email, phone))
                cursor.close()
                conn.commit()
                conn.close()
                return []


class ActionEmail(Action):

    def name(self) -> Text:
        return "email_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["email"]

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> None:

        email = tracker.get_slot('email')
        pattern = re.compile(r'^[\w]{1,19}@((163)|(qq)|(126)|(gmail)).((com)|(cn))$', re.I)
        e = pattern.match(str(email))
        if e is None:
            dispatcher.utter_message(text="{} is not a valid email".format(email))
            return [UserUtteranceReverted()]
        else:
            conn = sqlite3.connect("customer.db")
            cursor = conn.cursor()
            query1 = "CREATE TABLE IF NOT EXISTS customer (id integer PRIMARY KEY,email text NOT NULL, phone integer NOT NULL);"
            cursor.execute(query1)
            query = "SELECT * FROM customer WHERE email = ?"
            e = email,
            cursor.execute(query, e)
            if not cursor.fetchall():
                dispatcher.utter_message(text="Email address {} does not exist in the database".format(email))
                cursor.close()
                conn.commit()
                conn.close()
                return [UserUtteranceReverted()]
            else:
                cursor.close()
                conn.commit()
                conn.close()
                return []

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("I cannot understand")
        return [UserUtteranceReverted()]
