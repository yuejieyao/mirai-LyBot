from modules.conf import config
from typing import List
from aip import AipOcr

conf = config.getBaiduConf()


class BaiduUtils:

    def __init__(self) -> None:
        self.appId = conf['appId']
        self.apiKey = conf['apiKey']
        self.secretKkey = conf['secretKey']


class OcrUtil(BaiduUtils):

    def __init__(self) -> None:
        super().__init__()
        self.client = AipOcr(
            appId=self.appId, apiKey=self.apiKey, secretKey=self.secretKkey)

    def basicGeneralUrl(self, url: str) -> List[str]:
        options = {}
        options["detect_direction"] = "true"
        result = self.client.basicGeneralUrl(url, options=options)
        if 'words_result' in result:
            return [i['words'] for i in result['words_result']]
        return []
