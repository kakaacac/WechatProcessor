# -*- coding: utf-8 -*-
from lxml import etree


class XMLParser(object):
    def __init__(self, dictionary=None, xml_str=None):
        if dictionary:
            self.dictionary = dictionary
        if xml_str:
            self.xml_str = xml_str
            self.xml_elem = etree.fromstring(xml_str)

    def dict_to_xml_element(self, dictionary=None, root="xml"):
        d = dictionary if dictionary else self.dictionary
        assert isinstance(d, dict)

        elem = etree.Element(root)
        self.append_data(elem, d)

        return elem

    def append_data(self, xml_element, dictionary):
        for key, val in dictionary.items():
            sub_elem = etree.Element(key)
            if isinstance(val, dict):
                self.append_data(sub_elem, val)
                xml_element.append(sub_elem)
            elif isinstance(val, (list, set)):
                for item in val:
                    self.append_data(xml_element, {key: item})
            elif isinstance(val, tuple):
                if len(val) == 2 and val[1] == "CDATA":
                    sub_elem.text = etree.CDATA(val[0])
                    xml_element.append(sub_elem)
                else:
                    for item in val:
                        self.append_data(xml_element, {key: item})
            else:
                sub_elem.text = str(val)
                xml_element.append(sub_elem)

    def dict_to_xml(self, d=None, root="xml"):
        return etree.tounicode(self.dict_to_xml_element(d, root))

    def to_xml(self):
        return self.dict_to_xml(self.dictionary) if self.dictionary else None

    def xml_to_dict(self, xml_str=None):
        return self.xml_elem_to_dict(etree.fromstring(xml_str))

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