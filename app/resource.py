# -*- coding: utf-8 -*-
import datetime
from flask_restful import Resource, reqparse
from flask import make_response, request, jsonify

from .config import Config
from .utils.messager import WechatMessager
from .utils.redis import r
from .models import db, Message, get_cursor

__all__ = ('WechatMessageApi', 'FeedApi', 'FeedbackApi')

class WechatMessageApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("signature", location='args', store_missing=False)
        self.parser.add_argument("timestamp", location='args', store_missing=False)
        self.parser.add_argument("nonce", location='args', store_missing=False)

        self.messager = WechatMessager()

    # Called by Wechat to verify server's URL
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

        if self.messager.verify(args.get("signature"), args.get("timestamp"), args.get("nonce")):
            received_data = self.messager.extract_msg_to_dict(request.data,
                                                              args.get("msg_signature"),
                                                              args.get("timestamp"),
                                                              args.get("nonce"))
            user = received_data["FromUserName"]
            received_msg = received_data["Content"]
            received_time = datetime.datetime.fromtimestamp(int(received_data["CreateTime"]))

            message = Message(sender=user, msg_type=received_data['MsgType'], content=received_data['Content'],
                              wechat_msg_id=received_data['MsgId'], received_time=received_time)
            db.session.add(message)
            db.session.commit()

            if received_msg == "feed":
                self.add_feeding_task()
                reply = "Feeding task added."
            else:
                reply = "Hello!\nYour message: {}".format(received_msg)

            response = self.messager.get_response(reply, Config.WECHAT_CONFIG["wechat_id"], user)
            return make_response(response, 200)

        else:
            return make_response("Failed to verify message", 200)

    def add_feeding_task(self):
        r.set("feed", 1)


class FeedApi(Resource):
    def __init__(self):
        pass

    def get(self):
        task = r.getset("feed", 0)
        return make_response(str(task), 200)


class FeedbackApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        super().__init__()

    def post(self):
        self.parser.add_argument("text", location='form', store_missing=False)
        self.parser.add_argument("fb_type", location='form', store_missing=False)
        args = self.parser.parse_args()

        cur = get_cursor()
        text = ("%{}%".format(args.get("text", "")), )
        fb_type = int(args.get("fb_type", 0))
        if fb_type == 0:        # lesson content
            cur.execute("SELECT lesson_num, lesson_date, lesson_content, code FROM lesson INNER JOIN class "
                        "ON lesson.class_id=class.id WHERE lesson_content LIKE %s", text)
            result = [("{} -- {} ({})".format(row[3], row[0], row[1]), row[2]) for row in cur.fetchall()]
        elif fb_type == 1:      # homework
            cur.execute("SELECT lesson_num, lesson_date, homework, code FROM lesson INNER JOIN class "
                        "ON lesson.class_id=class.id WHERE homework LIKE %s", text)
            result = [("{} -- {} ({})".format(row[3], row[0], row[1]), row[2]) for row in cur.fetchall()]
        else:                   # personal feedback
            cur.execute("SELECT student_name, content from sentence where content LIKE %s", text)
            result = list(cur.fetchall())

        return jsonify({"result": result})
