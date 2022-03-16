import time
import queue
import json
from urllib import parse
from typing import Any
from threading import Thread
import websocket
import webbrowser

from .config import settings


CODE = "code"
AUTHORISATION_CODE = "authorization_code"
CLIENT_CREDENTIALS = "client_credentials"
REFRESH_TOKEN = "refresh_token"
SCOPE = "user-exec-command"


class ApiException(Exception):
    """Signals technical API error"""


class ApiClient:
    """
    API client
    """

    ws: websocket.WebSocketApp

    _receive_queue: queue.Queue[Any]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._receive_queue = queue.LifoQueue()
        self.ws_url = parse.urlunparse(parse.urlparse(settings.base_url)._replace(scheme="wss"))

    @staticmethod
    def authorise():
        """
        :return:
        """
        params = dict(
            response_type=CODE,
            client_id=settings.client_id,
            redirect_uri=settings.redirect_uri,
            scope=settings.scope,
        )

        webbrowser.open(f"{settings.base_url}{settings.auth_url}?{parse.urlencode(params)}")

    def connect(self) -> "ApiClient":
        self.ws = websocket.WebSocketApp(
            parse.urljoin(self.ws_url, settings.conversation_url),
            header={"Authorization": f"Bearer {settings.access_token}"},
            on_message=self._on_message,
        )

        Thread(target=self.ws.run_forever, daemon=True).start()
        while not (self.ws.sock and self.ws.sock.connected):
            time.sleep(0.1)

        return self

    def disconnect(self) -> "ApiClient":
        self.ws.close()
        return self

    def is_connected(self) -> bool:
        return self.ws and self.ws.sock.connected

    def send_text_command(self, text: str) -> str:
        if not self.is_connected():
            raise ApiException("Not connected")

        self._flush_receive_queue()
        command = {"type": "command", "command": text}
        self.ws.send(json.dumps(command))
        res = self._receive_queue.get()

        return res

    def _on_message(self, ws: websocket.WebSocketApp, message: str):
        self._receive_queue.put(message)

    def _flush_receive_queue(self):
        while not self._receive_queue.empty():
            self._receive_queue.get()
