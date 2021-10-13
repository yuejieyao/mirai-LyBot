from modules.utils.sqlCombiner import Sqlite
from modules.utils import log as Log
import datetime


class DataSource(Sqlite):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.__initSqlite()

    def isSign(self, qq: int):
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        if self.query('select count(*) from sign where user_qq=:user_qq and date=:date', {'user_qq': qq, 'date': t})[0][0] == 1:
            return True
        return False

    def sign(self, qq: int, sign_text: str):
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        return self.execute('insert into sign (user_qq,date,sign_text) values(?,?,?)', [(qq, t, sign_text)])

    def __initSqlite(self):
        rs = self.query(
            "select name from sqlite_master where type='table' order by name")
        if ('sign',) not in rs:
            # 字段send=0表示可发送,1表示各种原因屏蔽掉不发送
            self.execute("""
                create table sign
                (
                    id INTEGER PRIMARY KEY,
                    user_qq int,
                    date date,
                    sign_text text
                ) 
            """)
            Log.info(msg="[Plugin][Sign] create table sign success")
