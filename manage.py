# -*- coding: utf-8 -*-
from flask import Flask
from flask_restful import Api

from app.resource import WechatMessageApi, FeedApi
from app.models import db
from app.config import Config

app = Flask(__name__)

# Sqlalchemy config
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{user}:{password}@{host}:{port}/{database}".format(**Config.PG_CONFIG)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Restful api config
api = Api(app, prefix="/wechat")

api.add_resource(WechatMessageApi, "/message")
api.add_resource(FeedApi, "/feed")

if __name__ == '__main__':
    app.run(debug=True)

