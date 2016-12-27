# -*- coding: utf-8 -*-
import base64
import struct
import socket
from Crypto.Cipher import AES
from xml.etree.ElementTree import Element, tostring, fromstring

from WechatProcessor.config import Config
from .functions import hash_sha1, random_string, timestamp


class XMLParser(object):
    def __init__(self, dictionary=None, xml_str=None):
        if dictionary:
            self.dictionary = dictionary
        if xml_str:
            self.xml_str = xml_str
            self.xml_elem = fromstring(xml_str)

    def dict_to_xml_element(self, dictionary=None, root="xml"):
        d = dictionary if dictionary else self.dictionary
        assert isinstance(d, dict)

        elem = Element(root)
        self.append_data(elem, d)

        return elem

    def append_data(self, xml_element, dictionary):
        for key, val in dictionary.items():
            sub_elem = Element(key)
            if isinstance(val, dict):
                self.append_data(sub_elem, val)
                xml_element.append(sub_elem)
            elif isinstance(val, (tuple, list, set)):
                for item in val:
                    self.append_data(xml_element, {key: item})
            else:
                sub_elem.text = str(val)
                xml_element.append(sub_elem)

    def dict_to_xml(self, d=None, root="xml"):
        return tostring(self.dict_to_xml_element(d, root))

    def to_xml(self):
        return self.dict_to_xml(self.dictionary) if self.dictionary else None

    def xml_to_dict(self, xml_str=None):
        return self.xml_elem_to_dict(fromstring(xml_str))

    def xml_elem_to_dict(self, xml_elem=None):
        root = xml_elem if xml_elem is not None else self.xml_elem
        dictionary = {}
        for child in root:
            content = self.xml_elem_to_dict(child) if child.text is None else child.text
            if child.tag in dictionary:
                if isinstance(dictionary[child.tag], list):
                    dictionary[child.tag].append(content)
                else:
                    dictionary[child.tag] = [dictionary[child.tag], content]
            else:
                dictionary[child.tag] = content
        return dictionary

    def to_dict(self):
        return self.xml_to_dict(self.xml_str) if self.xml_str else None


class WechatMessager:
    RESPONSE_TEMPLATE = """
    <xml>
    <Encrypt><![CDATA[{encrypted_msg}]]></Encrypt>
    <MsgSignature><![CDATA[{signature}]]></MsgSignature>
    <TimeStamp>{timestamp}</TimeStamp>
    <Nonce><![CDATA[{nonce}]]></Nonce>
    </xml>
    """

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

        pad = ord(plain_text.decode("utf-8")[-1])
        content = plain_text[16:-pad]

        l = socket.ntohl(struct.unpack("I",content[:4])[0])
        content = content[4:4 + l]

        return content.decode("utf-8") if utf8 else content

    def encrypt(self, data):
        text = random_string(16).encode() + struct.pack("I", socket.htonl(len(data))) + data.encode() + self.app_id.encode()
        text = self.pkcs7encode(text)

        cryptor = AES.new(self.msg_key, AES.MODE_CBC, self.msg_key[:16])
        try:
            ciphertext = cryptor.encrypt(text)
            return base64.b64encode(ciphertext)
        except Exception as e:
            raise

    @staticmethod
    def pkcs7encode(data, block_size=32):
        num = block_size - (len(data) % block_size)
        pad = chr(num).encode()
        return data + pad * num

    def get_response(self, reply):
        nonce = random_string(16)
        ts = timestamp()

        encrypted_msg = self.encrypt(reply)
        sign = self.sign(nonce, ts, encrypted_msg.decode())

        response_data = self.RESPONSE_TEMPLATE.format(**{
            "encrypted_msg": encrypted_msg,
            "signature": sign,
            "timestamp": ts,
            "nonce": nonce
        })

        return response_data

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

