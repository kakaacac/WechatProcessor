# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse
from flask import make_response, request

from .config import Config
from .utils.messager import WechatMessager

__all__ = ('WechatMessageApi',)

class WechatMessageApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("signature", location='args', store_missing=False)
        self.parser.add_argument("timestamp", location='args', store_missing=False)
        self.parser.add_argument("nonce", location='args', store_missing=False)

        self.messager = WechatMessager()

    # Called by Wechat for verification of server's URL
    def get(self):
        self.parser.add_argument("echostr", location='args', store_missing=False)
        args = self.parser.parse_args()

        success = self.messager.verify(args.get("signature"),
                                       args.get("timestamp"),
                                       args.get("nonce"))

        rep = make_response(args.get("echostr"), 200) if success else make_response("", 400)
        rep.headers["Content-Type"] = 'text/plain'
        return rep

    def post(self):
        self.parser.add_argument("openid", location='args', store_missing=False)
        self.parser.add_argument("msg_signature", location='args', store_missing=False)
        args = self.parser.parse_args()
        print(request.data)
        if self.messager.verify(args.get("signature"), args.get("timestamp"), args.get("nonce")):
            return make_response("success", 200)
        else:
            return make_response("failed", 200)