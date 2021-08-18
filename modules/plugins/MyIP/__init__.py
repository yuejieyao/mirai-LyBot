from modules.conf import config
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain
from modules.http.miraiMessageRequest import MiraiMessageRequest
import requests


@MiraiMessagePluginProcessor.mirai_friend_message_plugin_register('myIP')
class MyIP:
    def process(self, chains: MessageChain, target: int,  quote: int):
        if str(target) == config.getMiraiConf(option='adminQQ'):
            if chains.asDisplay() == "myip":
                resp = requests.session().get(url="http://myip.ipip.net/")
                resp.raise_for_status()
                result = resp.content.decode('utf-8')
                print(result)
                MiraiMessageRequest().sendAdminMessage(msg=MessageChain([Plain(text=result)]))
