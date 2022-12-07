from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, UserUttered
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import BotUttered
import sqlite3
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
import sizes
from datetime import datetime
import time
from dateutil.parser import parse
# change this to the location of your SQLite file
path_to_db = "actions/example.db"


class ConvertSize(Action):
    def name(self) -> Text:
        return "action_convert_size"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        size_text = tracker.get_slot("size_text")

        dispatcher.utter_message(text=size_text)
        
        info = size_text.split()
        size_from = info[0]
        size_to = info[1]
        size = float(info[2])
        size_to_val = sizes.convert(size_from, size_to, size)

        dispatcher.utter_message(text=str(size_to_val))
        return [SlotSet("size_text", None)]

class ValidateFirstName(Action):
    def name(self) -> Text:
        return "action_validate_first_name"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:


        message = tracker.latest_message['text']

        if message[0] != message[0].upper():
            dispatcher.utter_message(text='Please enter your first name starting with a capital letter')
            return [SlotSet("first_name", None)]
        letters = "abcdefghijklmnopqrstuvwxyz"
        upper_letters = letters.upper()
        for m in message:
            if not ((m in letters) or (m in upper_letters)):
                dispatcher.utter_message(text='Use only letters for your first name')
                return [SlotSet("first_name", None)]

        return[]

class ValidateLastName(Action):
    def name(self) -> Text:
        return "action_validate_last_name"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message = tracker.latest_message['text']
        letters = "abcdefghijklmnopqrstuvwxyz"
        upper_letters = letters.upper()
        if message[0] != message[0].upper():
            dispatcher.utter_message(text='Please enter your last name starting with a capital letter')
            return [SlotSet("last_name", None)]
        for m in message:
            if not ((m in letters) or (m in upper_letters)):
                dispatcher.utter_message(text='Use only letters for your last name')
                return [SlotSet("last_name", None)]
        return[]

class ValidateDate(Action):
    def name(self) -> Text:
        return "action_validate_birth_date"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        m = tracker.latest_message['text']
        res = True
        try: 
            parse(m, fuzzy=False)
        except ValueError:
            res = False
                
        if res==False:
            dispatcher.utter_message(text='Please enter date in format YYYY-MM-DD')
            return[SlotSet("birth_date", None)]

        return[]

class Registration(Action):
    def name(self) -> Text:
        return "action_register"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        #add email and passord
        user_email = tracker.get_slot("email")
        user_password = tracker.get_slot("password")
        user_first_name = tracker.get_slot("first_name")
        user_last_name = tracker.get_slot("last_name")
        user_birth_date = tracker.get_slot("birth_date")
        user_phone_number = tracker.get_slot("phone_number")

        user_info = (user_email, user_password, user_first_name, user_last_name, user_birth_date, user_phone_number)
        
        cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?, ?)", user_info)
        
        connection.commit()
        connection.close()

        dispatcher.utter_message(template="utter_register_successful")
        return [
            SlotSet("email", None),
            SlotSet("password", None),
            SlotSet("first_name", None),
            SlotSet("last_name", None),
            SlotSet("birth_date", None),
            SlotSet("phone_number", None)
        ]


class ActionProductSearch(Action):
    def name(self) -> Text:
        return "action_product_search"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get slots and save as tuple
        shoe = [(tracker.get_slot("color")), (tracker.get_slot("size"))]

        # place cursor on correct row based on search criteria
        cursor.execute("SELECT * FROM inventory WHERE color=? AND size=?", shoe)
        
        # retrieve sqlite row
        data_row = cursor.fetchone()

        if data_row:
            # provide in stock message
            dispatcher.utter_message(template="utter_in_stock")
            connection.close()
            slots_to_reset = ["size", "color"]
            return [SlotSet(slot, None) for slot in slots_to_reset]
        else:
            # provide out of stock
            dispatcher.utter_message(template="utter_no_stock")
            connection.close()
            slots_to_reset = ["size", "color"]
            return [SlotSet(slot, None) for slot in slots_to_reset]

class SurveySubmit(Action):
    def name(self) -> Text:
        return "action_survey_submit"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(template="utter_open_feedback")
        dispatcher.utter_message(template="utter_survey_end")
        return [SlotSet("survey_complete", True)]


class OrderStatus(Action):
    def name(self) -> Text:
        return "action_order_status"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get email slot
        order_email = (tracker.get_slot("email"))

        # retrieve row based on email
        cursor.execute("SELECT * FROM orders WHERE order_email=?", order_email)
        data_row = cursor.fetchone()

        if data_row:
            # convert tuple to list
            data_list = list(data_row)

            # respond with order status
            dispatcher.utter_message(template="utter_order_status", status=data_list[5])
            connection.close()
            return []
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(template="utter_no_order")
            connection.close()
            return []


class CancelOrder(Action):
    def name(self) -> Text:
        return "action_cancel_order"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get email slot
        order_email = (tracker.get_slot("email"),)

        # retrieve row based on email
        cursor.execute("SELECT * FROM orders WHERE order_email=?", order_email)
        data_row = cursor.fetchone()

        if data_row:
            # change status of entry
            status = [("cancelled"), (tracker.get_slot("email"))]
            cursor.execute("UPDATE orders SET status=? WHERE order_email=?", status)
            connection.commit()
            connection.close()

            # confirm cancellation
            dispatcher.utter_message(template="utter_order_cancel_finish")
            return []
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(template="utter_no_order")
            connection.close()
            return []


class ReturnOrder(Action):
    def name(self) -> Text:
        return "action_return"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get email slot
        order_email = (tracker.get_slot("email"),)

        # retrieve row based on email
        cursor.execute("SELECT * FROM orders WHERE order_email=?", order_email)
        data_row = cursor.fetchone()

        if data_row:
            # change status of entry
            status = [("returning"), (tracker.get_slot("email"))]
            cursor.execute("UPDATE orders SET status=? WHERE order_email=?", status)
            connection.commit()
            connection.close()

            # confirm return
            dispatcher.utter_message(template="utter_return_finish")
            return []
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(template="utter_no_order")
            connection.close()
            return []

class GiveName(Action):
    def name(self) -> Text:
        return "action_give_name"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        evt = BotUttered(
            text = "my name is bot? idk", 
            metadata = {
                "nameGiven": "bot"
            }
        )

        return [evt]