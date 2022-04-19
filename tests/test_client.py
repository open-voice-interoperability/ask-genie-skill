import time
from genie.client import ApiClient


def test_authorize():
    ApiClient().authorise()


def test_get_token():
    r = ApiClient().get_token()
    assert r["access_token"].startswith("eyJ")


def test_send_text_command():
    client = ApiClient().connect()

    # Sleep a bit to receive all history
    time.sleep(1)

    response = client.send_text_command("How is the weather in Bonn?")
    assert "today in Bonn" in response
