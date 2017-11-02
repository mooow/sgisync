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

import pydrive.auth, pydrive.drive
from string import ascii_letters as letters, digits

CREDENTIALS = 'gdrive_credentials.json'

class GoogleDrive(object):
    def __init__(self):
        self.__drive_init__()

    def __drive_init__(self):
        self.gauth = pydrive.auth.GoogleAuth()
        self.gauth.LoadCredentialsFile(CREDENTIALS)
        if self.gauth.credentials is None:
            self.gauth.LocalWebserverAuth()
            self.gauth.SaveCredentialsFile(CREDENTIALS)
        self.drive = pydrive.drive.GoogleDrive(self.gauth)

    def resolve_path(self, path):
        parent = 'root'
        for p in path.split('/'):
            if len(p) == 0: continue
            try:
                gd_file = self.get(p, parent)[0] # Get only first element :)
                parent = gd_file['id']
            except IndexError: return None
        return parent

    def _normalize(self, string):
        forbidden = '\\\''
        res = ""
        for char in string:
            if char not in forbidden:
                res += char
        return res

    def _query(self, query):
        return self.drive.ListFile({'q': query, 'orderBy': 'recency'}).GetList()

    def get(self, name, parent):
        name = self._normalize(name)
        parent = self._normalize(parent)
        query = "title = '{0}' and '{1}' in parents".format(name, parent)
        return self._query(query)

    def from_id(self, id):
        id = self._normalize(id)
        obj = self.drive.CreateFile({'id': id})
        obj.FetchMetadata()
        return obj

    def upload(self, filename, parentID = 'root'):
        file1 = self.drive.CreateFile({'title': filename, 'parents': [{'id': parentID}]})
        file1.SetContentFile(filename)
        file1.Upload()

    def list_dir(self, dirID):
        res = []
        for file in self._query("'{0}' in parents and mimeType != 'application/vnd.google-apps.folder'".format(dirID)):
            res.append(file['title'])
        return res
