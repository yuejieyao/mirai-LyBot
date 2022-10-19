#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 签到功能抄自 https://github.com/Womsxd/AutoMihoyoBBS,感谢贡献者
@Date     :2022/01/17 15:37:19
@UpdateDate     :2022/10/18
@Author      :yuejieyao
@version      :1.0
"""
import copy
import hashlib
import json
import random
import string
import time
import uuid

import requests

from modules.utils import log


def hexdigest(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


def random_text(num: int) -> str:
    return ''.join(random.sample(string.ascii_lowercase + string.digits, num))


def timestamp() -> int:
    return int(time.time())


# 获取请求Header里的DS 当web为true则生成网页端的DS
def get_ds(web: bool) -> str:
    if web:
        n = 'yUZ3s0Sna1IrSNfk29Vo6vRapdOyqyhB'
    else:
        n = 'PVeGWIZACpxXZ1ibMVJPi9inCY4Nd4y2'
    i = str(timestamp())
    r = random_text(6)
    c = hexdigest("salt=" + n + "&t=" + i + "&r=" + r)
    return f"{i},{r},{c}"


# 获取请求Header里的DS(版本2) 这个版本ds之前见到都是查询接口里的
def get_ds2(q: str, b: str) -> str:
    n = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs'
    i = str(timestamp())
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    add = f'&b={b}&q={q}'
    c = hexdigest("salt=" + n + "&t=" + i + "&r=" + r + add)
    return f"{i},{r},{c}"


# 生成一个device id
def get_device_id(cookie: str) -> str:
    return str(uuid.uuid3(uuid.NAMESPACE_URL, cookie))


def getCompHeaders(headers, query: str = ''):
    _headers = copy.copy(headers)
    _headers.update({
        'DS': get_ds2(q=query, b='')
    })
    return _headers


class GenshinUtils:
    ACT_ID = 'e202009291139501'
    MihoyoBBS_Version = '2.38.1'
    REFERER_URL = 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6'
    AWARD_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?act_id={}'.format(ACT_ID)
    USER_AGENT = 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 f'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/{MihoyoBBS_Version} '

    ROLE_URL = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format('hk4e_cn')
    INFO_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?region={}&act_id={}&uid={}'
    SIGN_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'

    RECORD_INFO_URL = "https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index?server={}&role_id={}"
    RECORD_ABYSS_URL = "https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/spiralAbyss?schedule_type=1&server={}&role_id={}"
    RECORD_DAILY_URL = "https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote?server={}&role_id={}"

    def __init__(self, cookie: str) -> None:
        self.cookie = cookie
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'DS': get_ds(web=True),
            "x-rpc-channel": "miyousheluodi",
            'Origin': 'https://webstatic.mihoyo.com',
            'x-rpc-app_version': self.MihoyoBBS_Version,
            'User-Agent': self.USER_AGENT,
            'x-rpc-client_type': "5",  # 4=PC,5=Mobile Web
            'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true'
                       f'&act_id={self.ACT_ID}&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion',
            "Cookie": self.cookie,
            'x-rpc-device_id': get_device_id(self.cookie)
        }

    def getRole(self):
        """ 获取绑定的天空岛帐号信息 """
        resp = requests.get(url=self.ROLE_URL, headers=self.headers)
        resp.raise_for_status()
        res = resp.json()
        if 'retcode' in res and res['retcode'] == 0:
            for item in res['data']['list']:
                if item['region_name'] == '天空岛':
                    return item
        return None

    def getAwardInfo(self):
        resp = requests.get(url=self.AWARD_URL, headers=self.headers)
        resp.raise_for_status()
        res = resp.json()
        if 'retcode' in res and res['retcode'] == 0:
            return res['data']['awards']
        return None

    def getSignInfo(self, role=None):
        """ 获取帐号的今日签到情况 """
        if role is None:
            role = self.getRole()
        region = role['region']
        game_uid = role['game_uid']
        info_url = self.INFO_URL.format(region, self.ACT_ID, game_uid)
        resp = requests.get(url=info_url, headers=self.headers)
        resp.raise_for_status()
        res = resp.json()
        if 'retcode' in res and res['retcode'] == 0:
            return res['data']
        return None

    def get_validate(self, gt, challenge):
        header = {"Accept": "*/*",
                  "X-Requested-With": "com.mihoyo.hyperion",
                  "User-Agent": self.USER_AGENT,
                  "Referer": "https://webstatic.mihoyo.com/",
                  "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
                  }
        validate = ""
        req = requests.get(
            f"https://api.geetest.com/ajax.php?gt={gt}&challenge={challenge}&lang=zh-cn&pt=3&client_type=web_mobile",
            headers=header)
        if req.status_code == 200:
            data = json.loads(req.text.replace("(", "").replace(")", ""))
            if "success" in data["status"] and "success" in data["data"]["result"]:
                validate = data["data"]["validate"]
        return validate

    def sign(self, role=None):
        """ 签到 """
        if role is None:
            role = self.getRole()
        data = {
            'act_id': self.ACT_ID,
            'region': role['region'],
            'uid': role['game_uid']
        }

        for i in range(4):
            if i > 0:
                log.info('[Plugins][Genshin] sign verification: time %d/3' % i)
            resp = requests.post(url=self.SIGN_URL, headers=self.headers, json=data)
            resp.raise_for_status()
            if resp.status_code == 429:
                log.error("[Plugins][Genshin] Sign Error: 429 Too Many Requests,sleep 10s")
                time.sleep(10)
                continue
            res = resp.json()
            if 'retcode' in res and res['retcode'] == 0:
                if 'data' in res and 'success' in res['data'] and res['data']['success'] == 1:
                    log.info(msg="[Plugins][Genshin] start sign verification")
                    log.error(resp.text)
                    validate = self.get_validate(res["data"]["gt"], res["data"]["challenge"])
                    if validate != "":
                        self.headers["x-rpc-challenge"] = res["data"]["challenge"]
                        self.headers["x-rpc-validate"] = validate
                        self.headers["x-rpc-seccode"] = f'{validate}|jordan'
                    time.sleep(random.randint(6, 15))
                else:
                    return True
            else:
                log.error(msg=resp.text)
                return False
        return False

    def getRecordInfo(self, role=None):
        """ 获取游戏内基本信息 """
        if role is None:
            role = self.getRole()
        url = self.RECORD_INFO_URL.format(role['region'], role['game_uid'])
        resp = requests.get(url=url,
                            headers=getCompHeaders(self.headers, f"role_id={role['game_uid']}&server={role['region']}"))
        resp.raise_for_status()
        res = resp.json()
        if 'retcode' in res:
            if res['retcode'] == 0:
                return res['data']
            elif res['retcode'] == "10102":
                raise Exception("用户设置了隐私")
            elif res['retcode'] == "10101":
                raise Exception("已满30次查询上限,今日无法继续使用")
        else:
            log.error('[Plugins][Genshin] get RecordInfo failed: ' + resp.text)
            raise Exception("查询失败")

    def getRecordAbyss(self, role=None):
        """ 获取游戏内深渊信息 """
        if role is None:
            role = self.getRole()
        url = self.RECORD_ABYSS_URL.format(role['region'], role['game_uid'])
        resp = requests.get(url=url,
                            headers=getCompHeaders(self.headers,
                                                   f"role_id={role['game_uid']}&schedule_type=1&server={role['region']}"))
        resp.raise_for_status()
        res = resp.json()
        if 'retcode' in res:
            if res['retcode'] == 0:
                return res['data']
            elif res['retcode'] == "10102":
                raise Exception("用户设置了隐私")
            elif res['retcode'] == "10101":
                raise Exception("已满30次查询上限,今日无法继续使用")
        else:
            log.error('[Plugins][Genshin] get RecordInfo failed: ' + resp.text)
            raise Exception("查询失败")

    def getRecordDaily(self, role=None):
        """ 获取游戏内体力和远征信息 """
        if role is None:
            role = self.getRole()
        url = self.RECORD_DAILY_URL.format(role['region'], role['game_uid'])
        resp = requests.get(url=url,
                            headers=getCompHeaders(self.headers,
                                                   f"role_id={role['game_uid']}&server={role['region']}"))
        resp.raise_for_status()
        res = resp.json()
        if 'retcode' in res:
            if res['retcode'] == 0:
                return res['data']
            elif res['retcode'] == "10102":
                raise Exception("用户设置了隐私")
            elif res['retcode'] == "10101":
                raise Exception("已满30次查询上限,今日无法继续使用")
        else:
            log.error('[Plugins][Genshin] get RecordInfo failed: ' + resp.text)
            raise Exception("查询失败")
