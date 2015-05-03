import os.path

class Config(object):
    CSRF_ENABLED = True
    TESTING = False
    SECRET_KEY = 'you-will-never-guess'
    SECRET_KEY = 'someprivatestringhere'
    STORMPATH_API_KEY_FILE = os.path.expanduser('~/.apiKey.properties')
    STORMPATH_APPLICATION = 'taplists.beer'
    STORMPATH_ENABLE_USERNAME = True
    STORMPATH_ENABLE_GIVEN_NAME = False
    STORMPATH_ENABLE_SURNAME = False
    STORMPATH_ENABLE_MIDDLE_NAME = False
    STORMPATH_REQUIRE_USERNAME = True
    STORMPATH_REQUIRE_GIVEN_NAME = False
    STORMPATH_REQUIRE_MIDDLE_NAME = False
    STORMPATH_REQUIRE_SURNAME = False


class TestingConfig(Config):
    TESTING = True
