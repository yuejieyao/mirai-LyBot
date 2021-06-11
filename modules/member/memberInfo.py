from typing import List


class GroupInfo:
    id: int
    name: str
    permission: str

    def __init__(self, id: int, name: str, permission: str) -> None:
        self.id = id
        self.name = name
        self.permission = permission

    @staticmethod
    def fromJson(obj) -> 'GroupInfo':
        return GroupInfo(id=int(obj['id']), name=obj['name'], permission=obj['permission'])

    @staticmethod
    def fromJsonList(obj_list) -> List['GroupInfo']:
        return [GroupInfo.fromJson(i) for i in obj_list]


class FriendInfo:
    id: int
    nickname: str
    remark: str

    def __init__(self, id: int, nickname: str, remark: str) -> None:
        self.id = id
        self.nickname = nickname
        self.remark = remark

    @staticmethod
    def fromJson(obj) -> 'FriendInfo':
        return FriendInfo(id=int(obj['id']), nickname=obj['nickname'], remark=obj['remark'])

    @staticmethod
    def fromJsonList(obj_list) -> List['FriendInfo']:
        return [FriendInfo.fromJson(i) for i in obj_list]
