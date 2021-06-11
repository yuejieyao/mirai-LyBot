from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.message.messageChain import MessageChain


class MiraiMessageRequest:
    def __init__(self) -> None:
        self.httpRequest = MiraiHttpRequests()

    def sendGroupMessage(self, msg: MessageChain, target: int, quote: int = None):
        """
        @description : 发送群消息
        ---------
        @param : msg:消息,target:目标群号,quote:引用消息ID
        -------
        """

        data = {"sessionKey": self.httpRequest.sessionKey,
                "messageChain": msg.asJson(), "target": target}
        if quote:
            data.update({"quote": quote})
        response = self.httpRequest.post('sendGroupMessage', data=data)
        if response['code'] != 0:
            print('sendGroupMessage failed:')
            print(response)

    def sendFriendMessage(self, msg: MessageChain, target: int, quote: int = None):
        """
        @description : 发送好友消息
        ---------
        @param : msg:消息,target:目标好友QQ,quote:引用消息ID
        -------
        """

        data = {"sessionKey": self.httpRequest.sessionKey,
                "messageChain": msg.asJson(), "target": target}
        if quote:
            data.update({"quote": quote})
        response = self.httpRequest.post('sendFriendMessage', data=data)
        if response['code'] != 0:
            print('sendGroupMessage failed:')
            print(response)

    def recall(self, target: int):
        """
        @description : 撤回群员消息
        ---------
        @param : 目标消息id
        -------
        """

        data = {"sessionKey": self.httpRequest.sessionKey, "target": target}
        response = self.post('recall', data=data)
        if response['code'] != 0:
            print('recall failed')
