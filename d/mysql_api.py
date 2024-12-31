import pymysql

connection = pymysql.connect(
    host = "127.0.0.1",
    user = "root",
    password = "YCPS_Alex_MySQL_2024",
    database = "hy_txl",
    )
cursor = connection.cursor()

from flask import *

mysql = Flask("mysql")

@mysql.route("select")
def select():
    sql = request.args.get("sql")
    cursor.execute(sql)
    return cursor.fetchall()
