# encoding utf-8
# name:httpRequest.py
import threading
import time
import traceback

import requests

from modules.conf import config
from modules.utils import log


class MiraiHttpRequests:
    sessionKey: str
    host = 'http://%s:%s' % (config.getConf('mirai', 'server'), config.getConf('mirai', 'port'))
    verifyKey = config.getConf('mirai', 'verifyKey')
    botQQ = config.getConf('mirai', 'botQQ')

    _instance_lock = threading.Lock()

    def __new__(cls) -> 'MiraiHttpRequests':
        if not hasattr(MiraiHttpRequests, "_instance"):
            with MiraiHttpRequests._instance_lock:
                if not hasattr(MiraiHttpRequests, "_instance"):
                    MiraiHttpRequests._instance = object.__new__(cls)
        return MiraiHttpRequests._instance

    # def __init__(self) -> None:
    #     self.request = None

    def get(self, func):
        response = self.request.get(
            "%s/%s?sessionKey=%s" % (self.host, func, self.sessionKey))
        response.raise_for_status()
        return response.json()

    def post(self, func, data):
        headers = {'Content-Type': 'application/json'}
        response = self.request.post(
            url="%s/%s" % (self.host, func), json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def login(self):
        self.request = requests.session()
        last_session_key = config.getConf('mirai', 'sessionKey')
        if last_session_key:
            rs = self.post(
                'release', {'sessionKey': last_session_key, 'qq': self.botQQ})
            if rs['code'] == 0:
                log.info(msg=f"release success,sessionKey = {last_session_key}")
            else:
                log.error(msg=f"release error: sessionKey = {last_session_key}")
        while True:
            try:
                response = self.post('verify', {'verifyKey': self.verifyKey})
                self.sessionKey = response['session']
                response = self.post(
                    'bind', {'sessionKey': self.sessionKey, 'qq': self.botQQ})
                if response['code'] == 0:
                    log.info(msg=f'login success,sessionKey = {self.sessionKey}')
                    config.setConf('mirai', 'sessionKey', self.sessionKey)
                    break
            except:
                log.error(msg=traceback.format_exc())
                log.info(msg='login error ---- retry in 5 seconds')
                time.sleep(5)

    def release(self):
        try:
            rs = self.post(
                'release', {'sessionKey': self.sessionKey, 'qq': self.botQQ})
            if rs['code'] == 0:
                log.info(msg=f"release success,sessionKey = {self.sessionKey}")
                config.setConf('mirai', 'sessionKey', '')
            else:
                log.error(msg=f"release error: sessionKey = {self.sessionKey}")
        except:
            log.error(msg=traceback.format_exc())
