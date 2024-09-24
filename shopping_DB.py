import mysql.connector

class shopping_DB():
    def __init__(self, host, port=3306, user='root', password='', database='shopping_db'):
        self.shopping_db = mysql.connector.connect(
            host = host,
            port = port,
            user = user,
            password = password,
            database = database,
        )
        self.cursor = self.shopping_db.cursor()

    def CREATE_TABLE(self, sql):
        self.cursor.execute(sql)
        self.shopping_db.commit()
    
    def SELECT(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def TABLE_modify(self, sql, condition=None):
        if condition is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, condition)
        self.shopping_db.commit()
    
    def TABLE_modify_many(self, sql, condition=None):
        if condition is None:
            self.cursor.execute(sql)
        else:
            self.cursor.executemany(sql, condition)
        self.shopping_db.commit()
