# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid

db = SQLAlchemy()

class Message(db.Model):
    message_id = db.Column(UUID, primary_key=True)
    sender = db.Column(db.String(128), nullable=False)
    received_time = db.Column(db.DateTime(timezone=False))
    msg_type = db.Column(db.String(32))
    content = db.Column(db.Text)
    wechat_msg_id = db.Column(db.String(32))

    def __init__(self, sender, msg_type, content, wechat_msg_id, message_id=None, received_time=None):
        self.sender = sender
        self.msg_type = msg_type
        self.content = content
        self.wechat_msg_id = wechat_msg_id

        if message_id is not None:
            self.message_id = message_id
        else:
            self.message_id = str(uuid.uuid4())

        if received_time is not None:
            self.received_time = received_time