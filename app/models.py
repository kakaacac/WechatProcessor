# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Message(db.Model):
    message_id = db.Column(db.String(64), primary_key=True)
    sender = db.Column(db.String(128), nullable=False)
    received_time = db.Column(db.DateTime(timezone=False))
    msg_type = db.Column(db.String(32))
    content = db.Column(db.Text)
    wechat_msg_id = db.Column(db.String(32))