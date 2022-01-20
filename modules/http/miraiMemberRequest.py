from typing import List
from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.member.memberInfo import FriendInfo, GroupInfo, BotInfo, GroupMemberInfo


class MiraiMemberRequests:
    def __init__(self) -> None:
        self.httpRequest = MiraiHttpRequests()

    def getBotInfo(self) -> BotInfo:
        response = self.httpRequest.get('botProfile')
        return BotInfo.fromJson(response)


    def getFirendList(self) -> List[FriendInfo]:
        """ 获取好友列表 """

        response = self.httpRequest.get('friendList')
        if response['code'] == 0:
            return FriendInfo.fromJsonList(response)
        else:
            return []

    def getGroupList(self) -> List[GroupInfo]:
        """ 获取群列表 """

        response = self.httpRequest.get('groupList')
        if response['code'] == 0:
            return GroupInfo.fromJsonList(response['data'])
        else:
            return []

    def getGroupMemberInfo(self, group: int, qq: int) -> GroupMemberInfo:
        """获取群成员信息"""

        response = self.httpRequest.request.get('%s/%s?sessionKey=%s&target=%s&memberId=%s' %
                                                (self.httpRequest.host, 'memberProfile', self.httpRequest.sessionKey, group, qq))
        response.raise_for_status()
        return GroupMemberInfo.fromJson(response.json())