from modules.conf import config
from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.message.messageChain import MessageChain
from modules.utils import log


class MiraiMessageRequest:
    def __init__(self) -> None:
        self.httpRequest = MiraiHttpRequests()

    def sendAdminMessage(self, msg: MessageChain):
        """ 发送消息到管理员,管理员配置为conf文件中的adminQQ,可以用逗号分割多个管理员

        Param:
            msg (MessageChain): 消息链
        """
        admin_ids = config.getConf('mirai', 'adminQQ').split(',')
        for adminId in admin_ids:
            self.sendFriendMessage(msg=msg, target=adminId)

    def sendGroupMessage(self, msg: MessageChain, target: int, quote: int = None):
        """ 发送群消息

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
        log.info(msg=f"[SendGroupMessage][-> (GID){target}] {msg.asSerializationString()}")
        if response['code'] != 0:
            raise Exception(f'send group message failed:{str(response)}')

    def sendTempMessage(self, msg: MessageChain, target_group: int, target_qq: int, quote: int = None):
        """ 发送群临时消息

        Param:
            msg (MessageChain): 消息链
            target_group (int): 目标群号
            target_qq (int): 目标QQ号
            quote (int): 引用消息ID,可选,默认为None
        """
        data = {"sessionKey": self.httpRequest.sessionKey,
                "messageChain": msg.asJson(), "group": target_group, "qq": target_qq}
        if quote:
            data.update({"quote": quote})
        response = self.httpRequest.post('sendTempMessage', data=data)
        log.info(msg=f"[SendTempMessage][-> (GID){target_group}][-> (UID){target_qq}] {msg.asSerializationString()}")
        if response['code'] != 0:
            raise Exception(f'send group message failed:{str(response)}')

    def sendFriendMessage(self, msg: MessageChain, target: int, quote: int = None):
        """ 发送好友消息 

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
        log.info(msg=f"[SendFriendMessage][-> (UID){target}] {msg.asSerializationString()}")

    def recall(self, target: int):
        """ 撤回消息

        Param:
            target (int): 目标消息id
        """

        data = {"sessionKey": self.httpRequest.sessionKey, "target": target}
        response = self.httpRequest.post('recall', data=data)
        if response['code'] != 0:
            raise Exception('recall failed')
        log.info(msg=f"[Recall][-> (ID){target}]")
