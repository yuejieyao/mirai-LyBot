import signal
import sys
import traceback

from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.http.miraiWebSockets import MiraiWebSocketClient
from modules.schedule.miraiSchedule import MiraiScheduleProcessor
from modules.utils import log


def ctrl_c(signalnum, frame):
    log.info(f"Received {signalnum} {frame}")
    sys.exit(0)


def start():
    try:
        conn = MiraiHttpRequests()
        conn.login()

        websocket_client = MiraiWebSocketClient(conn.sessionKey)
        websocket_client.open()

        mirai_schedule = MiraiScheduleProcessor()
        mirai_schedule.start()
    except:
        log.error(msg=traceback.format_exc())
        start()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c)
    signal.signal(signal.SIGTERM, ctrl_c)
    start()
