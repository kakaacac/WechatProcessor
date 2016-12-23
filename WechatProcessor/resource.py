# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse

from .config import Config
from .functions import hash_sha1_string

__all__ = ('WechatMessageApi',)

class WechatMessageApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()

    # Called by Wechat for verification of server's URL
    def get(self):
        self.parser.add_argument("signature", location='args', store_missing=False)
        self.parser.add_argument("timestamp", location='args', store_missing=False)
        self.parser.add_argument("nonce", location='args', store_missing=False)
        self.parser.add_argument("echostr", location='args', store_missing=False)
        args = self.parser.parse_args()

        sign = hash_sha1_string("".join(sorted([args["timestamp"], args["nonce"], Config.WECHAT_CONFIG["token"]])))

        return (args["echostr"], 200) if sign == args["signature"] else (None, 400)

    def post(self):
        pass