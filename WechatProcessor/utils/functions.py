# -*- coding: utf-8 -*-
import hashlib
from string import ascii_letters, digits
import random
import time


def hash_md5(string):
    md5 = hashlib.md5()
    md5.update(string.encode("utf-8"))
    return md5.hexdigest()


def hash_sha1(string):
    md5 = hashlib.sha1()
    md5.update(string.encode("utf-8"))
    return md5.hexdigest()


def random_string(n):
    random.seed(time.time())
    return "".join(random.sample(ascii_letters + digits, n))


def timestamp():
    return str(int(time.time()))