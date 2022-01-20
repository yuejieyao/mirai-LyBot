from modules.utils.sqlCombiner import Sqlite
from modules.utils import log as Log


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
        res = self.query("select qq_id,cookie from bind where group_id=:group", {'group': group})
        return res

    def getCookie(self, group: int, qq: int):
        res = self.query("select cookie from bind where group_id=:group and qq_id=:qq", {'group': group, 'qq': qq})
        if len(res) > 0:
            return str(res[0][0])
        else:
            return None

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
            Log.info('[Plugin][Genshin] create table bind success')
