# -*- coding: utf-8 -*-
import base64
import struct
import socket
from Crypto.Cipher import AES

from app.config import Config
from .functions import hash_sha1, random_string, timestamp
from .xml_parser import XMLParser


class WechatMessager:
    def __init__(self, app_id=None, token=None, msg_key=None):
        self.app_id = Config.WECHAT_CONFIG["app_id"] if app_id is None else app_id
        self.token = Config.WECHAT_CONFIG["token"] if token is None else token

        key = Config.WECHAT_CONFIG["msg_key"] if msg_key is None else msg_key
        self.msg_key = base64.b64decode(key + "=")

        self.xml_parser = XMLParser()

    def sign(self, *args):
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            data = args[0]
        else:
            data = list(args)

        data.append(self.token)
        return hash_sha1("".join(sorted(data)))

    def verify(self, sign, *sign_args):
        return sign == self.sign(*sign_args)

    def decrypt(self, data, utf8=True):
        cryptor = AES.new(self.msg_key, AES.MODE_CBC, self.msg_key[:16])
        plain_text = cryptor.decrypt(data)

        pad = ord(plain_text.decode()[-1])
        content = plain_text[16:-pad]

        l = socket.ntohl(struct.unpack("I",content[:4])[0])
        content = content[4:4 + l]

        return content.decode() if utf8 else content

    def encrypt(self, data):
        text = random_string(16) + struct.pack("I", socket.htonl(len(data.encode()))).decode() + data + self.app_id
        encoded_text = self.pkcs7encode(text)

        try:
            cryptor = AES.new(self.msg_key, AES.MODE_CBC, self.msg_key[:16])
            ciphertext = cryptor.encrypt(encoded_text)
            return base64.b64encode(ciphertext)
        except Exception as e:
            raise

    @staticmethod
    def pkcs7encode(data, block_size=32):
        encoded_data = data.encode()
        num = block_size - (len(encoded_data) % block_size)
        pad = chr(num)
        return encoded_data + pad.encode() * num

    def get_response(self, content, from_user, to_user):
        nonce = random_string(16)
        ts = timestamp()

        reply = self.get_reply_xml(content, from_user, to_user, ts)
        encrypted_msg = self.encrypt(reply).decode()
        sign = self.sign(nonce, ts, encrypted_msg)

        response_data = {
            "Encrypt": (encrypted_msg, "CDATA"),
            "MsgSignature": (sign, "CDATA"),
            "TimeStamp": ts,
            "Nonce": (nonce, "CDATA")
        }

        return self.xml_parser.dict_to_xml(response_data)

    def get_reply_xml(self, content, from_user, to_user, timestamp):
        return self.xml_parser.dict_to_xml({
            "ToUserName": (to_user, "CDATA"),
            "FromUserName": (from_user, "CDATA"),
            "CreateTime": timestamp,
            "MsgType": ("text", "CDATA"),
            "Content": (content, "CDATA"),
        })

    def extract_msg(self, data, msg_sign, *sign_args):
        received_data = self.xml_parser.xml_to_dict(data)
        try:
            encrypted_data = received_data["Encrypt"]
            if self.verify(msg_sign, encrypted_data, *sign_args):
                return self.decrypt(base64.b64decode(encrypted_data))
            else:
                return None
        except KeyError as e:
            raise

    def extract_msg_to_dict(self, data, msg_sign, *sign_args):
        return self.xml_parser.xml_to_dict(self.extract_msg(data, msg_sign, *sign_args))

