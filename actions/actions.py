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
# change this to the location of your SQLite file
path_to_db = "actions/example.db"


def validate(user_email, user_first_name, user_second_name, user_phone_number):
    flag = 1
    if not re.match("[^@]+@[^@]+\.[^@]+", user_email):
        flag = 0
        print('Please enter the correct email')
    if user_first_name[0] != user_first_name[0].upper():
        flag = 0
        print('Please enter your name starting with a capital letter')
    if user_second_name[0] != user_second_name[0].upper():
        flag = 0
        print('Please enter your lastname starting with a capital letter')
    if carrier._is_mobile(number_type(phonenumbers.parse(number))) == False:
        flag = 0
        print('Plese enter the correct phone number')
    return flag
# action_convert_size

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
        return []

class RegistrationName(Action):
    def name(self) -> Text:
        return "action_fill_name"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="what is your name")

        message = tracker.latest_message['text']

        if message[0] != message[0].upper():
            dispatcher.utter_message(text='Please enter your name starting with a capital letter')
        
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
        # user_password = tracker.get_slot("password")
        # user_first_name = tracker.get_slot("first_name")
        # user_second_name = tracker.get_slot("second_name")
        # user_country = tracker.get_slot("country")
        user_phone_number = tracker.get_slot("phone_number")
        # user_info = (user_email, user_password, user_first_name, user_second_name, user_country, user_phone_number)

        # its_OK = validate(user_email)
        # if its_OK:
        #     cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?, ?)", user_info)    
        # else:
        #     pass
        #     # need to restart action
        
        user_info = (user_email, user_phone_number)
        cursor.execute("INSERT INTO user VALUES (?, ?)", user_info)
        
        connection.commit()
        connection.close()

        message = tracker.latest_message['text']
        if True: #correct(message):
            dispatcher.utter_message(template="utter_register_successful")
            return [
                UserUttered("name", parse_data={'intent':{'name': 'register_fill_name', 'confidence': 1.0}}),
                SlotSet("requested_slot", "name")]
        else:
            # slot intent register

            return []
        # dispatcher.utter_message(text=message)

        return []


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