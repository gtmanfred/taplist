import crypt
import random
import redis
import sys
from redis.sentinel import Sentinel
import json
import string
from flask_login import UserMixin

def create_user(username, password, roles):
    sentinel = Sentinel([('localhost', 26379)], socket_timeout=0.1)
    r = sentinel.master_for('mymaster', socket_timeout=0.1, db=1)
    salt = '$6$'
    for i in range(8):
        salt += random.choice(string.ascii_letters + string.digits)
    saltpass = crypt.crypt(password, salt)
    hashdict = {
        'username': username,
        'password': saltpass,
        'roles': roles
    }
    r.hmset('user_{0}'.format(username), hashdict)

class BarUser(UserMixin):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

        pool = redis.ConnectionPool(host='localhost', port=6379, db=1)
        self.r = redis.Redis(connection_pool=pool)
        item = self.r.hgetall('user_{0}'.format(username))
        self.roles = item.get('roles', '').split(',')
        if password is None:
            self.authenticated = False
        else:
            salt = ''.join(['$' + i for i in item['password'].split('$')[1:3]])
            self.authenticated = item['password'] == crypt.crypt(self.password, salt)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True if self.authenticated else False

    def is_anonymous(self):
        return False if self.authenticated else True

    def get_id(self):
        return self.username

if __name__ == '__main__':
    create_user(*sys.argv[1:])
