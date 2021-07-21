from typing import List
from modules.http.miraiHttpRequests import MiraiHttpRequests
from modules.member.memberInfo import FriendInfo, GroupInfo


class MiraiMemberRequests:
    def __init__(self) -> None:
        self.httpRequest = MiraiHttpRequests()

    def getFirendList(self) -> List[FriendInfo]:
        """获取好友列表"""

        response = self.httpRequest.get('friendList')
        if response['code'] == 0:
            return FriendInfo.fromJsonList(response)
        else:
            return []

    def getGroupList(self) -> List[GroupInfo]:
        """获取群列表"""

        response = self.httpRequest.get('groupList')
        if response['code'] == 0:
            return GroupInfo.fromJsonList(response['data'])
        else:
            return []
