from apscheduler.schedulers.blocking import BlockingScheduler
import pymysql
MYSQL_PASSWD = "YCPS_Alex_MySQL_2024"
connection = pymysql.connect(
    host = "127.0.0.1",
    user = "root",
    password = MYSQL_PASSWD,
    database = "hy_txl",
    )
cursor = connection.cursor()


import time
import random, string

def get_future_time(seconds: int) -> int:
    """
    获取指定秒数后的未来时间戳（以秒为单位）。
    
    :param seconds: 距离当前时间的秒数
    :return: 未来时间的 Unix 时间戳（int）
    """
    current_timestamp = int(time.time())  # 获取当前 Unix 时间戳
    future_timestamp = current_timestamp + seconds
    return future_timestamp


def random_str(length: int=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])
def set_random_key():
        """
        设置新的随机密码。
        :param new_key: 新的随机密码
        :param expires_in_seconds: 密码过期的时间（单位：秒）
        :return: status
        """
        connection.ping()
        expires_at = get_future_time(seconds=1200)
        cursor.execute("UPDATE admin_auth SET random_key=%s, expires_at=%s WHERE id=1", (random_str(), expires_at))
        connection.commit()
        return 700


scheduler = BlockingScheduler()

set_random_key()
scheduler.add_job(set_random_key, 'interval', seconds=600)


scheduler.start()