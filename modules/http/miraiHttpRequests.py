# encoding utf-8
# name:httpRequest.py
import requests
import time
import threading
from modules.conf import config
mirai_config = config.getMiraiConf()

host = 'http://%s:%s' % (mirai_config['server'], mirai_config['port'])
verifyKey = mirai_config['verifyKey']
botQQ = mirai_config['botQQ']


class MiraiHttpRequests:
    sessionKey: str
    _instance_lock = threading.Lock()

    def __new__(cls) -> 'MiraiHttpRequests':
        if not hasattr(MiraiHttpRequests, "_instance"):
            with MiraiHttpRequests._instance_lock:
                if not hasattr(MiraiHttpRequests, "_instance"):
                    MiraiHttpRequests._instance = object.__new__(cls)
        return MiraiHttpRequests._instance

    def __init__(self) -> None:
        pass

    def get(self, func):
        response = self.request.get(
            "%s/%s?sessionKey=%s" % (host, func, self.sessionKey))
        response.raise_for_status()
        return response.json()

    def post(self, func, data):
        headers = {'Content-Type': 'application/json'}
        response = self.request.post(
            url="%s/%s" % (host, func), json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def login(self):
        self.request = requests.session()
        last_sessionKey = config.getMiraiConf('sessionKey')
        print(last_sessionKey)
        if last_sessionKey:
            rs = self.post(
                'release', {'sessionKey': last_sessionKey, 'qq': botQQ})
            if rs['code'] == 0:
                print('release success:%s' % last_sessionKey)
            else:
                print('release error')
                print(rs)
        while True:
            try:
                response = self.post('verify', {'verifyKey': verifyKey})
                self.sessionKey = response['session']
                response = self.post(
                    'bind', {'sessionKey': self.sessionKey, 'qq': botQQ})
                if response['code'] == 0:
                    print('login success')
                    config.setMiraiConf('sessionKey', self.sessionKey)
                    break
            except Exception as e:
                print(e)
                print('login error -- relogin in 5 seconds')
                time.sleep(5)

    def release(self):
        try:
            rs = self.post(
                'release', {'sessionKey': self.sessionKey, 'qq': botQQ})
            if rs['code'] == 0:
                print('release success:%s' % self.sessionKey)
                config.setMiraiConf('sessionKey', '')
            else:
                print('release error')
                print(rs)
        except Exception as e:
            print('release error')
            print(e)
