from modules.plugins.miraiPlugin import MiraiMessagePluginProcessor
from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.http.miraiWebSockets import MiraiWebSocketClient
from modules.message.miraiMessageHandler import MiraiMessageHandler


def start():
    try:
        conn = MiraiHttpRequests()
        conn.login()

        websocket_client = MiraiWebSocketClient(conn.sessionKey)
        websocket_client.open()
    except:
        start()


if __name__ == '__main__':
    start()
