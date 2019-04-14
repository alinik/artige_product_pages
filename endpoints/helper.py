import codecs
from pprint import PrettyPrinter

def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def get_path(path):
    return path.as_posix() if isinstance(path, os.PathLike) else str(path)


get_std = lambda item: item.get('media_or_ad').get('images').get('standard_resolution').get('url')
get_thumb = lambda item: item.get('media_or_ad').get('images').get('thumbnail').get('url')
get_car_std = lambda item, n: item.get('media_or_ad').get('carousel_media')[n].get('images').get(
    'standard_resolution').get('url')
get_car_thumb = lambda item, n: item.get('media_or_ad').get('carousel_media')[n].get('images').get('thumbnail').get(
    'url')
get_cap = lambda item: item.get('media_or_ad').get('caption').get('text')
get_pic = lambda item: item.get('media_or_ad').get('user').get('profile_picture')
get_user = lambda item: {k: item.get('media_or_ad').get('user').get(k) for k in 'id username full_name'.split()}

def print_dict(dct, lvl=0, keys=None):
    sep = '- ' * lvl
    lvl += 1
    for k, v in sorted(dct.items(),
                       key=lambda x: 2 if type(x[1]) in (list, dict) else 0 if x[0] in ('id', 'pk') else 1):
        if isinstance(v, dict):
            print(sep, k, '{')
            print_dict(v, lvl)
            print(sep, '}', k)
        elif isinstance(v, list):
            print(sep, k, '[')
            for c, i in enumerate(v):
                print(c, end=':')
                print_dict(i, lvl)
            print(sep, ']', k)
        else:
            print('%s%s:\t%s' % (sep, k, v))

pp = PrettyPrinter(indent=2, width=120)
pprint = pp.pprint
