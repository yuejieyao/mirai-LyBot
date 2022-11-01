from modules.utils import log
from modules.utils.sqlCombiner import Sqlite


class DataSource(Sqlite):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.__initSqlite()

    def addBind(self, group: int, qq: int, cookie: str):
        return self.execute("insert into bind (group_id,qq_id,cookie) values(?,?,?)", [(group, qq, cookie)])

    def removeBind(self, group: int, qq: int):
        return self.execute("delete from bind where group_id=:group and qq_id=:qq", {'group': group, 'qq': qq})

    def exeistsBind(self, group: int, qq: int):
        res = self.query("select * from bind where group_id=:group and qq_id=:qq", {'group': group, 'qq': qq})
        if len(res) > 0:
            return True
        else:
            return False

    def getGroupBinds(self, group: int):
        res = self.query("select qq_id,cookie,ua from bind where group_id=:group", {'group': group})
        return res

    def getCookieAndUa(self, group: int, qq: int):
        res = self.query("select cookie,ua from bind where group_id=:group and qq_id=:qq", {'group': group, 'qq': qq})
        if len(res) > 0:
            return str(res[0][0]), str(res[0][1])
        else:
            return None

    def addResinRemind(self, group: int, qq: int):
        return self.execute("insert into resin_remind(group_id,qq_id) values(?,?)", [(group, qq)])

    def getResinRemind(self, group: int, qq: int):
        return self.query("select send,switch from resin_remind where group_id=:group and qq_id=:qq",
                          {'group': group, 'qq': qq})

    def existsResinRemind(self, group: int, qq: int):
        res = self.query("select * from resin_remind where group_id=:group and qq_id=:qq", {'group': group, 'qq': qq})
        if len(res) > 0:
            return True
        else:
            return False

    def openResinRemind(self, group: int, qq: int):
        return self.execute("update resin_remind set switch=1 where group_id=:group and qq_id=:qq",
                            {'group': group, 'qq': qq})

    def closeResinRemind(self, group: int, qq: int):
        return self.execute("update resin_remind set switch=0 where group_id=:group and qq_id=:qq",
                            {'group': group, 'qq': qq})

    def isCloseResinRemind(self, group: int, qq: int):
        res = self.query("select switch from resin_remind where group_id=:group and qq_id=:qq",
                         {'group': group, 'qq': qq})[0]
        if res[0] == 1:
            return False
        else:
            return True

    def isSend(self, group: int, qq: int):
        res = self.query("select send from resin_remind where group_id=:group and qq_id=:qq",
                         {'group': group, 'qq': qq})[0]
        if res[0] == 1:
            return True
        else:
            return False

    def setSend(self, group: int, qq: int):
        return self.execute("update resin_remind set send=1 where group_id=:group and qq_id=:qq",
                            {'group': group, 'qq': qq})

    def setNotSend(self, group: int, qq: int):
        return self.execute("update resin_remind set send=0 where group_id=:group and qq_id=:qq",
                            {'group': group, 'qq': qq})

    def __initSqlite(self):
        if not self.exists_table('bind'):
            # 字段send=0表示可发送,1表示各种原因屏蔽掉不发送
            self.execute("""
                create table bind
                (
                    id INTEGER PRIMARY KEY,
                    group_id int,
                    qq_id int,
                    cookie text
                )
            """)
            log.info('[Plugin][Genshin] create table bind success')
        if not self.exists_table('resin_remind'):
            self.execute("""
                create table resin_remind
                (
                    id INTEGER PRIMARY KEY,
                    group_id int,
                    qq_id int,
                    send int DEFAULT 0,
                    switch int DEFAULT 1
                )
            """)
            log.info('[Plugin][Genshin] create table resin_remind success')
