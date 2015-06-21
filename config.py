import os.path
import yaml

class Config(object):
    CSRF_ENABLED = True
    DEVEL = False
    SECRET_KEY = 'REPLACE'
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

    STORMPATH_ENABLE_FORGOT_PASSWORD = True
    _configfile = os.path.expanduser('~/config.yml')
    with open(_configfile) as yml:
        CONFIG = yaml.load(yml)['owners']

    LOCATIONS = []
    for owner, it in CONFIG.items():
        LOCATIONS.extend(it.get('locations', []))


class TestingConfig(Config):
    DEVEL = True
