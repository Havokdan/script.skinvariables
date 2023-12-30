# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import xml.etree.ElementTree as ET


"""

Module for converting xml based template config code into json

item (equivalent to a dictionary object)
list name=""
items mode="" name="" (equivalent to for_each)
condition
datafile
template
value name=""  (equivalent to dictionary with key as name attribute and value as contents)
"""


class Meta():
    def __init__(self, root, meta):
        self.root = root
        self.meta = meta

    def set_listtext(self, tag, key=None):
        value = [i.text for i in self.root.findall(tag)]
        if not value:
            return
        self.meta[key or tag] = value
        return value

    def set_itemtext(self, tag, key=None):
        value = next((i.text for i in self.root.findall(tag) if i.text), None)
        if not value:
            return
        self.meta[key or tag] = value
        return value

    def set_value(self):
        values = []
        for root in self.root.findall('value'):
            name = root.attrib['name']
            if not list(root):
                self.meta[name] = root.text
                continue
            values.append(Meta(root, self.meta.setdefault(name, {})))
        return values

    def set_items(self):
        root = next((i for i in self.root.findall('items')), None)
        if not root:
            return []

        for k, v in root.attrib.items():
            self.meta[k] = v

        items = []
        self.meta['for_each'] = []
        for item in root.findall('item'):
            meta = {}
            self.meta['for_each'].append(meta)
            items.append(Meta(item, meta))
        return items

    def set_lists(self):
        items = []
        self.meta['list'] = []
        for item in self.root.findall('list'):
            meta = {}
            pair = [item.attrib['name'], meta]
            self.meta['list'].append(pair)
            items.append(Meta(item, meta))
        if not items:
            del self.meta['list']
            return []
        return items


class XMLtoJSON():
    def __init__(self, filecontent):
        self.root = ET.fromstring(filecontent)
        self.meta = {}

    def get_meta(self):
        self.get_contents(Meta(self.root, self.meta))
        return self.meta

    def get_contents(self, meta):
        meta.set_itemtext('template')
        meta.set_listtext('datafile')
        meta.set_listtext('condition')
        for i in meta.set_value():
            self.get_contents(i)
        for i in meta.set_lists():
            self.get_contents(i)
        for i in meta.set_items():
            self.get_contents(i)


def xml_to_json(filecontent):
    return XMLtoJSON(filecontent).get_meta()
