from modules.utils.sqlCombiner import Sqlite
from modules.utils import log as Log

mirai_db = 'modules/resource/data/mirai.db'


class MiraiDataSource(Sqlite):
    def __init__(self) -> None:
        super().__init__(mirai_db)
        self.__initSqlite()

    def addPlugin(self, register_name: str, name: str, description: str, plugin_type: str = 'group'):
        if self.exists(table='plugin', column='register_name', value=register_name):
            return self.execute('update plugin set name=:name,description=:description where register_name=:register_name', {'name': name, 'description': description, 'register_name': register_name})
        else:
            return self.execute('insert into plugin (register_name,name,description,plugin_type) values(?,?,?,?)',
                                [(register_name, name, description, plugin_type)])

    def removePlugin(self, register_name: str):
        return self.execute('delete from plugin where register_name=:register_name', {'regisger_name', register_name})

    def openPlugin(self, register_name: str):
        return self.execute('update plugin set open=1 where register_name=:register_name', {'register_name': register_name})

    def closePlugin(self, register_name: str):
        return self.execute('update plugin set open=0 where register_name=:register_name', {'register_name': register_name})

    def openGroupPlugin(self, register_name: str, group: int):
        unopen = self.query("select unopen from plugin where register_name=:register_name",
                            {'register_name': register_name})[0][0]
        if str(group) in unopen:
            __unopen = str(unopen).split(',')
            __unopen.remove(str(group))
            unopen = ','.join(__unopen)
            return self.execute('update plugin set unopen=:unopen where register_name=:register_name', {'unopen': unopen, 'register_name': register_name})
        else:
            raise Exception(f'群{group}并未关闭插件{register_name}')

    def closeGroupPlugin(self, register_name: str, group: int):
        unopen = self.query("select unopen from plugin where register_name=:register_name",
                            {'register_name': register_name})[0][0]
        if str(group) not in unopen:
            if unopen == '':
                unopen = str(group)
            else:
                unopen = ','.join(str(unopen).split(',').append(str(group)))
            return self.execute('update plugin set unopen=:unopen where register_name=:register_name', {'unopen': unopen, 'register_name': register_name})
        else:
            raise Exception(f'群{group}已经关闭插件{register_name}')

    def existGroupPlugin(self, register_name: str):
        if self.query("select count(*) from plugin where register_name=:register_name and plugin_type='group'", {'register_name': register_name})[0][0] > 0:
            return True
        else:
            return False

    def isGroupPluginClose(self, register_name: str, group: int):
        unopen = self.query("select unopen from plugin where register_name=:register_name",
                            {'register_name': register_name})[0][0]
        return str(group) in unopen

    def getGroupPlugins(self, group: int):
        """ register_name,name,unopen """
        result = self.query("select register_name,name,unopen from plugin where plugin_type='group' and open=1")
        return [tuple((
            re[0],
            re[1],
            0 if str(group) in re[2] else 1,
        )) for re in result]

    def getGroupOpenedPlugins(self, group: int):
        """ register_name """
        result = self.query("select register_name from plugin where plugin_type='group' and unopen not like :like", {
                            'like': f'%{str(group)}%'})
        return [r[0] for r in result]

    def getDescription(self, register_name: str) -> str:
        return str(self.query("select description from plugin where register_name=:register_name", {'register_name': register_name})[0][0])

    def __initSqlite(self):
        rs = self.query(
            "select name from sqlite_master where type='table' order by name")
        if ('plugin',) not in rs:
            # 字段send=0表示可发送,1表示各种原因屏蔽掉不发送
            self.execute("""
                create table plugin
                (
                    id INTEGER PRIMARY KEY,
                    register_name text UNIQUE,
                    name text,
                    description text,
                    unopen text DEFAULT '',
                    open int DEFAULT 1,
                    plugin_type text 
                )
            """)
            Log.info(msg="[Mirai][Plugin] create table plugin success")
