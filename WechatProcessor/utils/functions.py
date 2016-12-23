# -*- coding: utf-8 -*-
import hashlib


def hash_md5_string(string):
    md5 = hashlib.md5()
    md5.update(string.encode("utf-8"))
    return md5.hexdigest()

def hash_sha1_string(string):
    md5 = hashlib.sha1()
    md5.update(string.encode("utf-8"))
    return md5.hexdigest()
