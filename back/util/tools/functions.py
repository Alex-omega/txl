import hashlib
import random
import string

def encrypt(data, algorithm='sha256'):
    hash_object = hashlib.new(algorithm)
    hash_object.update(data.encode('utf-8'))
    hash_value = hash_object.hexdigest()
    return hash_value

def random_str(length: int=32):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))