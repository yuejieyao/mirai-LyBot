#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 所有用到的接口地址和调用方式全部参考了以下项目:https://github.com/sirodeneko/genshin-sign,https://github.com/Azure99/GenshinPlayerQuery,十分感谢作者的贡献
@Date     :2022/01/17 15:37:19
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


class GenshinUtils:
    ACT_ID = 'e202009291139501'
    REFERER_URL = 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6'
    AWARD_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?act_id={}'.format(ACT_ID)
    USER_AGENT = 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0'

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
            'Origin': 'https://webstatic.mihoyo.com',
            'User-Agent': self.USER_AGENT,
            'Referer': self.REFERER_URL,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion',
            'Cookie': cookie
        }

    def getCompHeaders(self, query: str = ''):
        headers = copy.copy(self.headers)
        headers.update({
            'x-rpc-device_id': str(uuid.uuid3(
                uuid.NAMESPACE_URL, self.cookie)).replace('-', '').upper(),
            # 1:  ios
            # 2:  android
            # 4:  pc web
            # 5:  mobile web
            'x-rpc-client_type': '5',
            'x-rpc-app_version': '2.11.1' if query else '2.3.0',
            'DS': self.getDs(query)
        })
        return headers

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
        resp = requests.get(url=info_url, headers=self.getCompHeaders())
        resp.raise_for_status()
        res = resp.json()
        if 'retcode' in res and res['retcode'] == 0:
            return res['data']
        return None

    def sign(self, role=None):
        """ 签到 """
        if role is None:
            role = self.getRole()
        data = {
            'act_id': self.ACT_ID,
            'region': role['region'],
            'uid': role['game_uid']
        }
        resp = requests.post(url=self.SIGN_URL, headers=self.getCompHeaders(),
                             data=json.dumps(data, ensure_ascii=False))
        resp.raise_for_status()
        res = resp.json()
        if 'retcode' in res and res['retcode'] == 0:
            return True
        else:
            log.error(msg=resp.text)
            return False

    def getRecordInfo(self, role=None):
        """ 获取游戏内基本信息 """
        if role is None:
            role = self.getRole()
        url = self.RECORD_INFO_URL.format(role['region'], role['game_uid'])
        resp = requests.get(url=url, headers=self.getCompHeaders(f"role_id={role['game_uid']}&server={role['region']}"))
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
        resp = requests.get(url=url, headers=self.getCompHeaders(
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
        resp = requests.get(url=url, headers=self.getCompHeaders(f"role_id={role['game_uid']}&server={role['region']}"))
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

    def hexdigest(self, text):
        md5 = hashlib.md5()
        md5.update(text.encode())
        return md5.hexdigest()

    def getDs(self, query: str = ''):
        if query:
            # v2.11.1
            n = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs'
            i = str(int(time.time()))
            r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
            b = ''
            q = query
            c = self.hexdigest('salt=' + n + '&t=' + i + '&r=' + r + '&b=' + b + '&q=' + q)
            return f'{i},{r},{c}'
        else:
            # v2.3.0-web @povsister & @journey-ad
            n = 'h8w582wxwgqvahcdkpvdhbh2w9casgfl'
            i = str(int(time.time()))
            r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
            c = self.hexdigest("salt=" + n + "&t=" + i + "&r=" + r)
            return f"{i},{r},{c}"
