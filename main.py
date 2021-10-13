from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.http.miraiWebSockets import MiraiWebSocketClient
from modules.schedule.miraiSchedule import MiraiScheduleProcessor
from modules.utils import log as Log
import traceback


def start():
    try:
        conn = MiraiHttpRequests()
        conn.login()
    except Exception:
        Log.error(msg=traceback.format_exc())
        start()
    else:
        websocket_client = MiraiWebSocketClient(conn.sessionKey)
        websocket_client.open()

        miraiSchedule = MiraiScheduleProcessor()
        miraiSchedule.start()


if __name__ == '__main__':
    start()
