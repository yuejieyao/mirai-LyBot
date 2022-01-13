from typing import List


class BotInfo:
    nickname: str
    email: str
    age: int
    level: int
    sign: str
    sex: str

    def __init__(self, nickname: str, email: str, age: int, level: int, sign: str, sex: str) -> None:
        self.nickname = nickname
        self.email = email
        self.age = age
        self.level = level
        self.sign = sign
        self.sex = sex

    @staticmethod
    def fromJson(obj) -> 'BotInfo':
        return BotInfo(nickname=obj['nickname'], email=obj['email'], age=obj['age'], level=obj['level'], sign=obj['sign'], sex=obj['sex'])
    


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
