import crypt
import random
import redis
import string
from flask_login import UserMixin

class BarUser(UserMixin):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

        pool = redis.ConnectionPool(host='localhost', port=6379, db=1)
        self.r = redis.Redis(connection_pool=pool)
        if username is None or password is None:
            self.authenticated = False
            self.roles = []
        else:
            item = json.loads(r.hmget('user_{0}'.format(username)).decode())
            salt = ''.join(['$' + i for i in item['password'].split('$')[1:3]])
            self.authenticated = item['password'] == crypt.crypt(self.password, salt)
            self.roles = item['roles'].split(',') if self.is_authenticated else []

    def is_authenticated(self):
        return True

    def is_active(self):
        return True if self.authenticated else False

    def is_anonymous(self):
        return False if self.authenticated else True

    def get_id(self):
        return self.username
