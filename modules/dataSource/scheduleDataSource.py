from modules.utils.sqlCombiner import Sqlite
from modules.utils import log as Log
import datetime
import uuid
import pickle
import traceback


class DataSource(Sqlite):

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.__initSqlite()

    def add_timing_remind(self, date, content: str, target: int, group: int):
        id = str(uuid.uuid1())
        self.execute("insert into remind (id,date,content,target,send_group) values(?,?,?,?,?)",
                     [(id, date, content, target, group)])
        return id

    def get_remind_less_than_now(self):
        return self.query("select id,date,content,target,send_group from remind where date>:date and send=0", {"date": datetime.datetime.now()})

    def set_send(self, id: str):
        return self.execute("update remind set send=1 where id=:id", {"id": id})

    def __initSqlite(self):
        if not self.exists_table('remind'):
            # 字段send=0表示可发送,1表示各种原因屏蔽掉不发送
            self.execute("""
                create table remind
                (
                    remind_id INTEGER PRIMARY KEY,
                    id text,
                    date date,
                    content text,
                    target int,
                    send_group int,
                    send int DEFAULT 0
                )
            """)
            Log.info(msg="[Plugin][Remind] create table remind success")
