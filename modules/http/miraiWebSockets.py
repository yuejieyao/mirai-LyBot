import json
import time
from threading import Thread

import websocket

from modules.conf import config
from modules.message.miraiMessageHandler import MiraiMessageHandler
from modules.utils import log

botQQ = config.getConf('mirai', 'botQQ')
verifykey = config.getConf('mirai', 'verifyKey')
messageHandler = MiraiMessageHandler()


class MiraiWebSocketClient:
    def __init__(self, session_key: str) -> None:
        self.url = f"ws://{config.getConf('mirai', 'server')}:{config.getConf('mirai', 'port')}/all?sessionKey={session_key}&verifyKey={verifykey}&qq={botQQ}"

    def on_open(self):
        log.info(msg='websocket open success')

        def loop():
            time.sleep(2)

        Thread(target=loop).start()

    def on_close(self, close_status_code, close_msg):
        raise Exception('websocket closed')

    def on_error(self, error):
        raise error

    def on_message(self, message):
        if isinstance(message, str):
            message = json.loads(message)
        messageHandler.onMessage(message['data'])

    def open(self, on_open=on_open, on_close=on_close, on_error=on_error, on_message=on_message):
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(
            self.url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
        Thread(target=ws.run_forever).start()
        # self.run_forever()
