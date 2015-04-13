import crypt
import sqlite3
import os
import random
import string

class BarUser(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.location = location

        dbfile = os.path.expanduser('~/users.db')
        self.conn = sqlite3.connect(dbfile)
        self.conn = sqlite.Row
        self.c = self.conn.cursor()
        self.db = self.c.execute('select * from users where username="{0}";'.format(self.username))
        item = self.db.fetchone()
        salt = ''.join(['$' + i for i in item.split('$')[:2]])
        self.authenticated = item['password'] == crypt.crypt(self.password, salt)
        self.roles = item['roles'].split(',') if self.authenticated else ''

    def set_password(self, newpassword):
        salt = '$6$'
        for i in range(8):
            salt += random.choice(string.ascii_letters + string.digits)
        saltpass = crypt.crypt(newpassword, salt)
        self.c.execute('update users set password="{0}" where username="{1}";'.format(saltpass, username)
