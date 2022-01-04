from modules.utils.sqlCombiner import Sqlite
from .rssUtils import RssUtils
from modules.utils import log as Log


class DataSource(Sqlite):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.__initSqlite()
        self.utils = RssUtils()

    def getNew(self, url: str):
        rss = self.utils.getLatestRss(url=url)
        if not self.exists(table='rss', column='rss_id', value=rss[0]):
            self.execute("insert into rss(rss_id,title,description,img,link,date) values(?,?,?,?,?,?)", [rss])
        return dict(rss_id=rss[0], title=rss[1], description=rss[2], img=rss[3], link=rss[4])

    def getMultNew(self, url: str):
        rsses = self.utils.getLatest10Rss(url=url)
        rdata = []
        for rss in rsses:
            rdata.append(dict(rss_id=rss[0], title=rss[1], description=rss[2], img=rss[3], link=rss[4]))
            if not self.exists(table='rss', column='rss_id', value=rss[0]):
                self.execute("insert into rss(rss_id,title,description,img,link,date) values(?,?,?,?,?,?)", [rss])
        return rdata

    def sub(self, url: str, group: int):
        try:
            title = self.utils.getChannel(url=url)
            if self.query('select count(*) from follow where url=:url and follow_group=:follow_group', {'url': url, 'follow_group': group})[0][0] > 0:
                raise Exception(f'该rss已订阅,请勿重复订阅')
            return self.execute('insert into follow(title,url,follow_group) values(?,?,?)', [(title, url, group)])
        except Exception as e:
            raise e

    def showSub(self, group: int):
        """return list[id,title]"""
        rs = self.query('select id,title from follow where follow_group=:follow_group', {'follow_group': group})
        return rs

    def getSubUrls(self):
        rs = self.query("select url from follow group by url")
        return [i[0] for i in rs]

    def getFollowers(self, url: str):
        rs = self.query("select follow_group from follow where url=:url", {"url": url})
        return [i[0] for i in rs]

    def unSub(self, id):
        if self.exists(table='follow', column='id', value=id):
            return self.execute('delete from follow where id=:id', {'id': id})
        return False

    def isSend(self, rss_id: int, group: int) -> bool:
        if self.query('select count(*) from send where rss_id=:rss_id and send_group=:send_group', {'rss_id': rss_id, 'send_group': group})[0][0] > 0:
            return True
        return False

    def setSend(self, rss_id: int, group: int):
        return self.execute("insert into send (rss_id,send_group) values(?,?)", [(rss_id, group)])

    def __initSqlite(self):
        if not self.exists_table('rss'):
            # 字段send=0表示可发送,1表示各种原因屏蔽掉不发送
            self.execute("""
                create table rss
                (
                    id INTEGER PRIMARY KEY,
                    rss_id text,
                    title text,
                    description text,
                    img text,
                    link text,
                    date date,
                    send int DEFAULT 0
                )
            """)
            Log.info('[Plugin][RSS] create table rss success')
        if not self.exists_table('follow'):
            self.execute("""
                create table follow
                    (
                        id INTEGER PRIMARY KEY,
                        title text,
                        url text,
                        follow_group int
                    )
            """)
            Log.info('[Plugin][RSS] create table follow success')
        if not self.exists_table('send'):
            # 发送记录
            self.execute("""
                create table send
                    (
                        id INTEGER PRIMARY KEY,
                        rss_id text,
                        send_group int
                    )
            """)
            Log.info('[Plugin][RSS] create table send success')
