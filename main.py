from modules.plugins.miraiPlugin import MiraiMessagePluginProcessor
from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.http.miraiWebSockets import MiraiWebSocketClient
from modules.message.miraiMessageHandler import MiraiMessageHandler


def start():
    try:
        conn = MiraiHttpRequests()
        conn.login()
    except Exception as e:
        print(e)
        start()
    else:
        websocket_client = MiraiWebSocketClient(conn.sessionKey)
        websocket_client.open()


if __name__ == '__main__':
    start()
