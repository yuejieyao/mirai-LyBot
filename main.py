from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.http.miraiWebSockets import MiraiWebSocketClient
from modules.schedule.miraiSchedule import MiraiScheduleProcessor


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

        miraiSchedule = MiraiScheduleProcessor()
        miraiSchedule.start()


if __name__ == '__main__':
    start()
