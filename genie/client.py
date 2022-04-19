import time
import queue
import json
from urllib import parse
from typing import Any
from threading import Thread
import httpx
import websocket
import webbrowser

from .config import settings


CODE = "code"
AUTHORIZATION_CODE = "authorization_code"
CLIENT_CREDENTIALS = "client_credentials"
REFRESH_TOKEN = "refresh_token"
SCOPE = "user-exec-command"

CONNECT_TIMEOUT = 10
SLEEP_TIME = 0.1


class ApiException(Exception):
    """Signals technical API error"""


class ApiClient:
    """
    API client
    """

    ws: websocket.WebSocketApp = None

    _receive_queue: queue.Queue[Any]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._receive_queue = queue.LifoQueue()
        self.ws_url = parse.urlunparse(parse.urlparse(settings.base_url)._replace(scheme="wss"))

    @staticmethod
    def authorise():
        params = dict(
            response_type=CODE,
            client_id=settings.client_id,
            redirect_uri=settings.redirect_uri,
            scope=SCOPE,
        )

        webbrowser.open(f"{settings.base_url}{settings.auth_url}?{parse.urlencode(params)}")

    @staticmethod
    def get_token():
        url = f"{settings.base_url}{settings.token_url}"
        params = dict(
            grant_type=AUTHORIZATION_CODE,
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            redirect_uri=settings.redirect_uri,
            code=settings.authorization_code,
        )

        with httpx.Client() as client:
            r = client.post(url, data=params)
            return r.json()

    def connect(self) -> "ApiClient":
        self.ws = websocket.WebSocketApp(
            parse.urljoin(self.ws_url, settings.conversation_url),
            header={"Authorization": f"Bearer {settings.access_token}"},
            on_message=self._on_message,
        )

        will_wait = CONNECT_TIMEOUT
        Thread(target=self.ws.run_forever, daemon=True).start()
        while not (self.ws.sock and self.ws.sock.connected):
            if (will_wait := will_wait - SLEEP_TIME) <= 0:
                raise ApiException("Time-out connecting to Genie cloud. Token expired?")
            time.sleep(SLEEP_TIME)

        return self

    def disconnect(self) -> "ApiClient":
        self.ws.close()
        return self

    def is_connected(self) -> bool:
        return self.ws and self.ws.sock and self.ws.sock.connected

    def send_text_command(self, text: str) -> str:
        if not self.is_connected():
            raise ApiException("Not connected")

        self._flush_receive_queue()
        command = {"type": "command", "text": text}
        self.ws.send(json.dumps(command))

        return self._retrieve_text_answer()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.disconnect()

    def _on_message(self, ws: websocket.WebSocketApp, message: str):
        self._receive_queue.put(message)

    def _flush_receive_queue(self):
        while not self._receive_queue.empty():
            self._receive_queue.get()

    def _retrieve_text_answer(self):
        while data := self._receive_queue.get():
            try:
                res = json.loads(data)
                if res["type"] == "text":
                    return res["text"]
            except json.JSONDecodeError:
                pass
