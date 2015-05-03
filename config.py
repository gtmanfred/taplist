import os.path

class Config(object):
    CSRF_ENABLED = True
    TESTING = False
    SECRET_KEY = 'you-will-never-guess'
    SECRET_KEY = 'someprivatestringhere'
    STORMPATH_API_KEY_FILE = os.path.expanduser('~/.apiKey.properties')
    STORMPATH_APPLICATION = 'taplists.beer'

class TestingConfig(Config):
    TESTING = True
