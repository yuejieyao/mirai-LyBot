from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.http.miraiWebSockets import MiraiWebSocketClient
from modules.schedule.miraiSchedule import MiraiScheduleProcessor
from modules.utils import log as Log
import traceback
import signal
import os

def ctrl_c(signalnum,frame):
		os._exit(0)

def start():
    try:
        conn = MiraiHttpRequests()
        conn.login()

        websocket_client = MiraiWebSocketClient(conn.sessionKey)
        websocket_client.open()

        miraiSchedule = MiraiScheduleProcessor()
        miraiSchedule.start()
    except Exception:
        Log.error(msg=traceback.format_exc())
        start()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c) 
    signal.signal(signal.SIGTERM, ctrl_c)
    start()
