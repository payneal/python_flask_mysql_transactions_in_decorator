from mysql.connector.pooling import MySQLConnectionPool  # noqa
from mysql.connector import connect  # NOQA
import mysql


class mysqlConnectorPool():
    def __init__(self):
        self.logger = {}
        self.dbConfig = {"database": "idk",
                         "user": "technicity",
                         "password": "technicity"}
        self.total_pools = 1
        self.pool_size = 32
        self.all_cnxpool = {}
        self.all_cnxpool[1] = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool{}".format(self.total_pools),
            pool_size=self.pool_size,
            **self.dbConfig)

    def startQuery(self):
        try:
            cnx1 = self.all_cnxpool[self.total_pools].get_connection()
            cursor = cnx1.cursor()
            return cnx1, cursor
        except Exception as e:  # noqa
            # print "error= {}".format(str(e))
            self.total_pools = self.total_pools + 1
            self.all_cnxpool[self.total_pools] = mysql.connector.pooling.MySQLConnectionPool(  # noqa
                pool_name="mypool{}".format(self.total_pools),
                pool_size=self.pool_size,
                **self.dbConfig)
            return self.startQuery()

    def grabAll(self, cursor, conn):
        hold = {}
        cursor.execute("SELECT * FROM idkman;")
        for num, x in enumerate(cursor, start=1):
            hold[num] = x
        cursor.close()
        conn.close()
        return hold

    def all_pending_transactions(self, cursor, conn):
        hold = {}
        cursor.execute("XA RECOVER;")
        for num, x in enumerate(cursor, start=1):
            hold[num] = x
        cursor.close()
        conn.close()
        return hold

    def start_transaction(self, xid, cursor):
        try:
            call = "XA START '{}';".format(xid)
            cursor.execute(call)
            return cursor
        except:
            return False

    def end_transaction(self, xid, cursor):
        try:
            call1 = "XA END '{}';".format(xid)
            call2 = "XA PREPARE '{}';".format(xid)
            cursor.execute(call1)
            cursor.execute(call2)
        except:
            return False

    def insert(self, cursor, name):
        try:
            cursor.execute('insert into idkman values("{}");'.format(name))
            return cursor
        except:
            return False

    def delete(self, cursor, name):
        try:
            cursor.execute('delete from idkman where name="{}";'.format(
                name))
            return cursor
        except:
            return False

    def rollBack_transaction(self, cursor, xid):
        try:
            call = "XA ROLLBACK '{}';".format(xid)
            cursor.execute(call)
            return True
        except:
            return False

    def commit_transaction(self, cursor, xid):
        try:
            call = "XA COMMIT '{}';".format(xid)
            cursor.execute(call)
            return True
        except:
            return False

    def closeConnection(self, cursor, connection):
        cursor.close()
        connection.commit()
        connection.close()
