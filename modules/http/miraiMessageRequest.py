from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.message.messageChain import MessageChain
from modules.conf import config
from modules.utils import log as Log


class MiraiMessageRequest:
    def __init__(self) -> None:
        self.httpRequest = MiraiHttpRequests()

    def sendAdminMessage(self, msg: MessageChain):
        """发送消息到管理员,管理员配置为conf文件中的adminQQ,可以用逗号分割多个管理员

        Param:
            msg (MessageChain): 消息链
        """
        adminIds = config.getMiraiConf('adminQQ').split(',')
        for adminId in adminIds:
            self.sendFriendMessage(msg=msg, target=adminId)

    def sendGroupMessage(self, msg: MessageChain, target: int, quote: int = None):
        """发送群消息

        Param:
            msg (MessageChain): 消息链
            target (int): 目标群号
            quote (int): 引用消息ID,可选,默认为None
        """
        data = {"sessionKey": self.httpRequest.sessionKey,
                "messageChain": msg.asJson(), "target": target}
        if quote:
            data.update({"quote": quote})
        response = self.httpRequest.post('sendGroupMessage', data=data)
        if response['code'] != 0:
            raise Exception(f'send group message failed:{str(response)}')
        Log.info(msg=f"[SendGroupMessage][-> (GID){target}] {msg.asSerializationString()}")

    def sendFriendMessage(self, msg: MessageChain, target: int, quote: int = None):
        """发送好友消息 

        Param:
            msg (MessageChain): 消息链
            target (int): 目标好友QQ号
            quote (int): 引用消息ID,可选,默认为None
        """
        data = {"sessionKey": self.httpRequest.sessionKey,
                "messageChain": msg.asJson(), "target": target}
        if quote:
            data.update({"quote": quote})
        response = self.httpRequest.post('sendFriendMessage', data=data)
        if response['code'] != 0:
            raise Exception('send friend message failed')
        Log.info(msg=f"[SendFriendMessage][-> (UID){target}] {msg.asSerializationString()}")

    def recall(self, target: int):
        """撤回消息

        Param:
            target (int): 目标消息id
        """

        data = {"sessionKey": self.httpRequest.sessionKey, "target": target}
        response = self.httpRequest.post('recall', data=data)
        if response['code'] != 0:
            raise Exception('recall failed')
        Log.info(msg=f"[Recall][-> (ID){target}]")
