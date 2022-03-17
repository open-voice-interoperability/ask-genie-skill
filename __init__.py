from mycroft import MycroftSkill, intent_handler
from mycroft.messagebus.message import Message
from mycroft.util import LOG
from adapt.intent import IntentBuilder

from .genie.client import ApiClient

LANG = "de"
NO_INTENT = "no.intent"
ASK = "ask"
LAUNCH = "launch"
STOP = "stop"


class AskGenie(MycroftSkill):

    client: ApiClient

    def __init__(self):
        super().__init__()
        self.client = ApiClient()

    @intent_handler(IntentBuilder("AskIntent").require("AskKeyword").require("utterance").build())
    def handle_ask(self, message: Message):
        """Send a single query"""
        LOG.info("Message: %s", message.serialize())
        utterance = message.data["utterance"]
        self.speak_dialog(ASK, message.data)
        with ApiClient() as client:
            client.connect()
            response = client.send_text_command(utterance)
            LOG.info("Answer: %s", response)
            self.speak_dialog(response)

    @intent_handler(IntentBuilder("LaunchIntent").require("LaunchKeyword").build())
    def handle_launch(self, message: Message):
        """Connects client"""
        LOG.info("Message: %s", message.serialize())
        self.client.connect()
        LOG.info("Connected to: %s", repr(self.client))
        self.speak_dialog(LAUNCH)

    @intent_handler(IntentBuilder("StopIntent").require("StopKeyword").build())
    def handle_stop(self, message: Message):
        """Disconnects client"""
        LOG.info("Message: %s", message.serialize())
        self.client.disconnect()
        self.speak_dialog(STOP)

    def converse(self, message=None):
        """Handles conversation"""
        LOG.info("Message: %s", message.serialize())

        try:
            utterance = message.data["utterances"][0]
        except (IndexError, TypeError):
            return False

        if not self.client.is_connected() or self.voc_match(utterance, "StopKeyword"):
            return False

        response = self.client.send_text_command(utterance)
        self.speak_dialog(response)

        return True


def create_skill():
    return AskGenie()
