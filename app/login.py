import crypt
import sqlite3
import os
import random
import string
from flask_login import UserMixin

class BarUser(UserMixin):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

        dbfile = os.path.expanduser('/home/taplist/users.db')
        self.conn = sqlite3.connect(dbfile)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        if username is None or password is None:
            self.authenticated = False
            self.roles = []
        else:
            self.db = self.c.execute('select * from users where username="{0}";'.format(self.username))
            item = self.db.fetchone()
            salt = ''.join(['$' + i for i in item['password'].split('$')[1:3]])
            self.authenticated = item['password'] == crypt.crypt(self.password, salt)
            self.roles = item['roles'].split(',') if self.is_authenticated else []

    def set_password(self, newpassword):
        salt = '$6$'
        for i in range(8):
            salt += random.choice(string.ascii_letters + string.digits)
        saltpass = crypt.crypt(newpassword, salt)
        self.c.execute('update users set password="{0}" where username="{1}";'.format(saltpass, username))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True if self.authenticated else False

    def is_anonymous(self):
        return False if self.authenticated else True

    def get_id(self):
        return self.username
