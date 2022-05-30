import sqlite3
from collections import namedtuple


def __dict_factory(cursor, row):
    """Returns sqlite rows as dict."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def __namedtuple_factory(cursor, row):
    """Returns sqlite rows as named tuples."""
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)


class Sqlite:
    def __init__(self, path: str, mode='list') -> None:
        """ 初始化sqlite

        Param:
            path (str): sqlite文件路径
            mode (str): 设定结果返回模式,可以为list,dict,nametuple,默认为list
        """

        self.conn = sqlite3.connect(path)
        if mode == 'dict':
            self.conn.row_factory = __dict_factory
        if mode == 'nametuple':
            self.conn.row_factory = __namedtuple_factory
        self.cur = self.conn.cursor()

    def exists(self, table: str, column: str, value) -> bool:
        rs = self.query(
            f"select {column} from  {table} where {column}=:value", {'value': value})
        if len(rs) > 0:
            return True
        return False

    def exists_table(self, name: str) -> bool:
        rs = self.query(f"SELECT * FROM sqlite_master WHERE TYPE='table' AND name=:name", {'name': name})
        if len(rs) > 0:
            return True
        return False

    def execute(self, sql: str, parameters=None) -> bool:
        """ 执行增删改

        Param:
            sql (str): sql语句
            parameters (list/tuple) : 使用参数化sql时需传入此参数
        Returns:
            执行成功返回true
        """

        try:
            if parameters:
                if type(parameters) is list:
                    self.cur.executemany(sql, parameters)
                else:
                    self.cur.execute(sql, parameters)
            else:
                self.cur.execute(sql)
            if self.conn.total_changes > 0:
                self.conn.commit()
                return True
            else:
                return False

        except Exception as e:
            raise e

    def query(self, sql: str, parameters=None) -> list:
        """ 执行sql查询
        
        Param:
            sql (str): sql语句
            parameters (tuple) : 使用参数化sql时需传入此参数
        Returns:

        """
        if parameters:
            self.cur.execute(sql, parameters)
        else:
            self.cur.execute(sql)
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()
