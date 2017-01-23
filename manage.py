# -*- coding: utf-8 -*-
from flask import Flask
from flask_restful import Api

from app import WechatMessageApi

app = Flask(__name__)
api = Api(app, prefix="/wechat")

api.add_resource(WechatMessageApi, "/message")

if __name__ == '__main__':
    app.run(debug=True)

