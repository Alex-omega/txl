import hashlib
import random
import string
import time

def encrypt(data, algorithm='sha256'):
    hash_object = hashlib.new(algorithm)
    hash_object.update(data.encode('utf-8'))
    hash_value = hash_object.hexdigest()
    return hash_value

def random_str(length: int=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])


def get_current_time() -> int:
    """
    获取指定秒数后的未来时间戳（以秒为单位）。
    
    :param seconds: 距离当前时间的秒数
    :return: 未来时间的 Unix 时间戳（int）
    """
    current_timestamp = int(time.time())  # 获取当前 Unix 时间戳
    return current_timestamp