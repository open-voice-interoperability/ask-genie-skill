import time
import pytest
from genie.client import ApiClient


def test_send_text_command():
    client = ApiClient().connect()

    # Sleep a bit to receive all history
    time.sleep(1)

    response = client.send_text_command("How is the weather in Bonn?")
    assert response.text[:35] in (
        "Hier kommt die Vorhersage für heute",
        "In der nächsten Stunde bleibt es in",
        "Hier kommt das aktuelle Wetter: In ",
    )
