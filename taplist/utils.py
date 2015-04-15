import collections

def convert(data):
    if isinstance(data, basestring):
        return data.decode('utf8')
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

def get_colors(location, config):
    for owner, its in config.items():
        if location in its['locations']:
            return its.get('colors', {})
    return {}
