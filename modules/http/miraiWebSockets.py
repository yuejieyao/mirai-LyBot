
import time
import json
import websocket
from modules.conf import config
from modules.message.miraiMessageHandler import MiraiMessageHandler
from threading import Thread

botQQ = config.getMiraiConf('botQQ')
verifykey = config.getMiraiConf('verifyKey')
messageHandler = MiraiMessageHandler()


class MiraiWebSocketClient:
    def __init__(self, sessionKey: str) -> None:
        self.url = f"ws://{config.getMiraiConf('server')}:{config.getMiraiConf('port')}/message?sessionKey={sessionKey}&verifyKey={verifykey}&qq={botQQ}"

    def on_open(ws):
        print('websocket opened')

        def loop():
            time.sleep(2)
        Thread(target=loop).start()

    def on_close(ws, close_status_code, close_msg):
        raise Exception('websocket closed')

    def on_error(ws, error):
        raise error

    def on_message(ws, message):
        if isinstance(message, str):
            message = json.loads(message)
        messageHandler.onMessage(message['data'])

    def open(self, on_open=on_open, on_close=on_close, on_error=on_error, on_message=on_message):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(
            self.url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
        Thread(target=ws.run_forever).start()
        # ws.run_forever()
