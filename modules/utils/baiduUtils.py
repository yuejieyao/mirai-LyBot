from re import template
from modules.conf import config
from typing import List
from aip import AipOcr
import random
import hashlib
import requests


class BaiduUtils:
    def __init__(self) -> None:
        pass


class OcrUtil(BaiduUtils):
    """文字识别"""

    def __init__(self) -> None:
        super().__init__()
        conf = config.getBaiduOcrConf()
        self.appId = conf['appId']
        self.apiKey = conf['apiKey']
        self.secretKkey = conf['secretKey']
        self.client = AipOcr(
            appId=self.appId, apiKey=self.apiKey, secretKey=self.secretKkey)

    def basicGeneralUrl(self, url: str) -> List[str]:
        options = {}
        options["detect_direction"] = "true"
        result = self.client.basicGeneralUrl(url, options=options)
        if 'words_result' in result:
            return [i['words'] for i in result['words_result']]
        return []


class TranslateUtil(BaiduUtils):
    """翻译"""

    def __init__(self) -> None:
        super().__init__()
        conf = config.getBaiduTranConf()
        self.appId = conf['appId']
        self.secretKkey = conf['secretKey']

    def translate(self, keyword: str, to: str) -> str:

        trans_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        slat = random.randint(0, 100)
        m = hashlib.md5()
        temp = self.appId+keyword+str(slat)+self.secretKkey
        if isinstance(temp, str):
            temp = temp.encode('utf8')
        m.update(temp)
        sign = m.hexdigest()
        data = {
            'q': keyword,
            'from': 'auto',
            'to': to,
            'appid': self.appId,
            'salt': slat,
            'sign': sign,
        }
        response = requests.session().post(trans_url, data=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
            elif 'error_code' in result:
                raise Exception(f"百度翻译接口调用失败,ErrorCode:{result['error_code']}")
            else:
                raise Exception("百度翻译接口调用失败:未知错误")
        else:
            raise Exception("百度翻译接口调用失败")
