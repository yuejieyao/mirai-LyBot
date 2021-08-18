import sqlite3


class Sqlite:
    def __init__(self, path: str) -> None:
        self.conn = sqlite3.connect(path)
        self.cur = self.conn.cursor()

    def exists(self, table, column, value) -> bool:
        rs = self.query(
            f"select {column} from  {table} where {column}=:value", {'value': value})
        if len(rs) > 0:
            return True
        else:
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
            print(e)
            return False

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
