import time
from genie.client import ApiClient


def test_send_text_command():
    client = ApiClient().connect()

    # Sleep a bit to receive all history
    time.sleep(1)

    response = client.send_text_command("How is the weather in Bonn?")
    assert "today in Bonn" in response
