#!/usr/bin/env python3

# This file is part of SgiSync
# Copyright (C) 2017 Lorenzo Mureu <mureulor@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import traceback
import os
import requests
import lxml.html
import json
import smtplib
from sys import stderr

DEFINES_FILE = "defines.json"
CONF_FILE = "sgidl.cfg"
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

class SgiDownloader:
    def __init__(self):
        self.__dict__.update(json.load(open(DEFINES_FILE, 'r')))
        self.set_magazine(list(self.magazines.keys())[0])
        self.session = requests.Session()
        self.session.headers['User-Agent'] = USER_AGENT

    def set_magazine(self, name):
        if name not in self.magazines:
            raise ValueError("SgiDl.set_magazine(): {0} is not a valid magazine name.".format(name))
        self.cur_magazine = name

    def _login_url(self):
        return self._url_fmt(self._mag()['login_page'])

    def _mag_list_url(self):
        return self._url_fmt(self._mag()['mag_list_page'])

    def _mag(self):
        return self.magazines[self.cur_magazine]

    def _url_fmt(self, page):
        return self._mag()['base_url_fmt'].format(page)

    def load_issues(self):
        global html
        html = lxml.html.fromstring(self.session.get(self._mag_list_url()).content)
        self.issues = {}
        for magazine in html.xpath(self._mag()['xpath']['magazines']):
            title = magazine.xpath(self._mag()['xpath']['extract_title'])[0].strip().replace(
                *self._mag()['xpath']['title_replace'])
            url = magazine.xpath(self._mag()['xpath']['extract_url'])[0]
            self.issues[title] = url

    def list(self):
        print("List of available magazines:")
        i = 1
        for key in self.issues.keys():
            print("[{0:3d}] - {1}".format(i, key))
            i += 1

    def download(self, title):
        url = self._url_fmt(self.issues[title])
        mime = self.session.head(url).headers['Content-Type']
        if  mime != 'application/x-download':
            print("Skipping {}: Content-Type={}".format(title, mime))
            return None

        print("Downloading {0} from {1} into {2}".format(title, url, fname))
        obj = self.session.get(url).content
        try:
            pdf = open(fname, "wb")
            pdf.write(obj)
            pdf.close()
        except:
            traceback.print_exc()
            print("Could not write `{0}`".format(fname), file=stderr)
        return fname

    def download_until(self, nid):
        ids = list(self.issues.keys())[:nid]
        for ref in ids:
            self.download(ref)

    def login(self):
        self.session.post(self._login_url(), data=self._mag()['login_post'])

    def get_magazines(self):
        return list( self.magazines.keys())

    def loadconf(self):
        if os.path.exists(CONF_FILE):
            fp = open(CONF_FILE, "r")
            self._mag()['login_post'].update(json.loads(fp.read()))
            fp.close()
        else:
            self._mag()['login_post']['user'] = input("Username: ")
            self._mag()['login_post']['password'] = input("Password: ")
            fp = open(CONF_FILE, "w")
            fp.write(json.dumps(self._mag()['login_post']))
            fp.close()

    def __test__(self, i=1):
        self.loadconf()
        self.login()
        self.load_issues()
        self.list()
        self.download_until(i)
