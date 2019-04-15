from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.timezone import now

from .apps import EndpointsConfig
from artige_product_pages.users.models import InstagramAccount
# Create your models here.
from .helper import *
from config.settings.base import MEDIA_ROOT, ROOT_DIR

import datetime
import json
import logging
from operator import itemgetter
from pathlib import Path

from .libs.instagram_private_api.instagram_private_api import (
    MediaRatios, Client, ClientError, ClientLoginError,
    ClientCookieExpiredError, ClientLoginRequiredError,
    ClientCompatPatch, MediaTypes,
    __version__ as client_version)
from .libs.instagram_private_api_extensions.instagram_private_api_extensions import media
from .libs.instagram_private_api_extensions.instagram_private_api_extensions import pagination


_logger = logging.getLogger(__name__)
cache_root = Path( ROOT_DIR ) / 'cache'
if not cache_root.is_dir():
    cache_root.mkdir()


class InstagramAccount(InstagramAccount):
    key = r'insta'
    insta_cache = cache_root / key
    if not insta_cache.is_dir():
        insta_cache.mkdir()
    _debug = False
    cache = models.BooleanField(default=True)
    private = JSONField(default=dict)
    cookie = JSONField(default=dict)
    # insta_user = models.CharField(max_length=128)
    # password = models.CharField(max_length=256)
    # insta_id = models.PositiveIntegerField()

    def __init__(self, username, password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = None
        self.cookie_expiry = None
        self.private = {'password': password}
        self.insta_user = username
        self._usercache = self.insta_cache / username

        if kwargs.get('debug', False):
            self.logger = logging.getLogger('%s%s' % (self.key, self.insta_user))
            self.debug = True
        if kwargs.get('cache', True) or self.debug:
            self.cache = True
            if not self._usercache.is_dir():
                self._usercache.mkdir()
        else:
            self.cache = False

    def login(self, force=False):
        self.logger.info('Creating a new session for user %s', self.insta_user)
        if not force and (self._session or self.cookie):
            try:
                self.load_session()
                return True
            except:
                self.logger.debug('Session expired')
        password = self.private.get('password')
        if not password:
            raise ClientLoginRequiredError('Password required %s', self.insta_user)
        self.logger.debug('Trying to re-login')
        try:
            login_dict = {}
            if self._session:
                self.logger.debug('Reuse existing settings')
                login_dict['user_agent'] = self._session.user_agent
                login_dict['device_id'] = self._session.device_id
            self.logger.debug('Client version: {0!s}'.format(client_version))
            session = Client(
                self.insta_user, password,
                **login_dict,
                on_login=lambda x: self.onlogin_callback(x)
            )
        except ClientLoginError as e:
            self.logger.error('ClientLoginError {0!s}'.format(e))
            raise e
        except ClientError as e:
            self.logger.error('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            raise e
        except Exception as e:
            self.logger.error('Unexpected Exception: {0!s}'.format(e))
            raise e
        self.logger.info('Session for user %s is created', self.insta_user)
        self._session = session
        return True

    def load_session(self):
        self.logger.info('Loading an existing session for user %s', self.insta_user)
        self.logger.debug('Client version: {0!s}'.format(client_version))
        session = None
        try:
            if self.cookie:
                cached_settings = self.cookie
                self.logger.info('Reusing settings')
            else:
                raise ClientLoginRequiredError('cookie has not ben saved', code=-1)
            # reuse auth settings
            session = Client(self.insta_user, None, settings=cached_settings)
        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            self.logger.warning('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))
            # Login expired
            # Do relogin but use default ua, keys and such
            self.login(force=True)
        except ClientLoginError as e:
            self.logger.error('ClientLoginError {0!s}'.format(e))
            raise e
        except ClientError as e:
            self.logger.error('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            raise e
        except Exception as e:
            self.logger.error('Unexpected Exception: {0!s}'.format(e))
            raise e

        # Show when login expires
        self.cookie_expiry = session.cookie_jar.auth_expires
        self.logger.info(
            'Cookie Expiry: {0!s}'.format(
                datetime.datetime.fromtimestamp(self.cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))
        self._session = session
        return True

    def post_media(self, image, caption, aspect_ratios=MediaRatios.standard, **kwargs):
        '''
        Posts a picture to instagram
        :param image: image uri
        :param caption: image caption
        :param aspect_ratios: aspect ration to adjust the image
        :param kwargs: additional insta post keys
        :return: dict
        '''
        save_path = self.get_cache()
        uri = get_path(image)
        photo_data, photo_size = media.prepare_image(uri, aspect_ratios=aspect_ratios, save_path=save_path)
        self._session.post_photo(photo_data, photo_size, caption=caption, **kwargs)

    def post_photo_story(self, image):
        '''
        Posts a picture to story
        :param image: image uri
        :return: dict
        '''
        save_path = self.get_cache()
        aspect_ratios = MediaRatios.reel
        uri = get_path(image)
        photo_data, photo_size = media.prepare_image(uri, aspect_ratios=aspect_ratios,
                                                     save_path=save_path)
        self._session.post_photo_story(photo_data, photo_size)

    def post_video(self, image, caption, aspect_ratios=MediaRatios.standard, **kwargs):
        uri = get_path(image)
        vid_data, vid_size, vid_duration, vid_thumbnail = media.prepare_video(
            uri, aspect_ratios=aspect_ratios)
        self._session.post_video(vid_data, vid_size, vid_duration, vid_thumbnail, caption=caption, **kwargs)

    def post_video_story(self, image, aspect_ratios=MediaRatios.reel, **kwargs):
        uri = get_path(image)
        vid_data, vid_size, vid_duration, vid_thumbnail = media.prepare_video(
            uri, aspect_ratios=aspect_ratios)
        self._session.post_video_story(vid_data, vid_size, vid_duration, vid_thumbnail)

    def iterate(self, func, args, data_key='items', cursor_key='max_id', next_cursor_key='next_max_id', wait=3,
                max=0):
        """
           A helper method to iterate over a feed/listing api call

            .. code-block:: python

                from endpoints import Config
                from endpoints import Instagram
                settings = Config()
                api = Instagram(username, None).get_session()
                items = []
                for item in api.iterate('user_feed', args={'user_id': '2958144170'}, max=10):
                    user = self.get_user(item)
                    print(user)
                ''
           :param func: function call
           :param args: dict of arguments to pass to func
           :param data_key: param name for the result items, e.g. 'items'
           :param cursor_key: param name for the cursor, e.g. 'max_id'
           :param next_cursor_key: param name for the cursor, e.g. 'next_max_id'
           :param wait: interval in seconds to sleep between api calls
           :param max: if provided, defines the maximum number of items to return
           :yield an item iterator
           """
        fn = getattr(self._session, func)
        start = 0
        get_data = itemgetter(data_key)
        get_cursor = itemgetter(next_cursor_key)
        for results in pagination.page(fn=fn, args=args, cursor_key=cursor_key, get_cursor=get_cursor, wait=wait):
            # print_dict(results)
            data = get_data(results)
            if data:
                self.logger.debug('method %s, number of %s: %d, %s', func, data_key, len(data), data)
                for i, v in enumerate(data, start=start):
                    yield v
                    if max and i >= max:
                        self.logger.debug('totally %d %s returned', i, data_key)
                        return
                start += len(data)

    def search_tags(self, pattern, max=0):
        '''
        iterates over tags starting with `pattern`
        :param pattern: tag pattern
        :param max: maximum number of tags to return
        :return: tag iterator
        '''
        rank_token = self._session.generate_uuid()
        has_more = True
        count = 0
        while has_more and rank_token:
            results = self._session.tag_search(pattern, rank_token)
            tag_results = results.get('results', [])
            has_more = results.get('has_more')
            rank_token = results.get('rank_token')
            if len(tag_results) > 0:
                for r in tag_results:
                    count += 1
                    if max and count > max:
                        has_more = False
                        break
                    yield r
        return None

        rank_token = Client.generate_uuid()
        has_more = True
        tag_results = []
        while has_more and rank_token and len(tag_results) < 60:
            results = session.tag_search(
                'cats', rank_token, exclude_list=[t['id'] for t in tag_results])
            tag_results.extend(results.get('results', []))
            has_more = results.get('has_more')
            rank_token = results.get('rank_token')
        _logger.debug(json.dumps([t['name'] for t in tag_results], indent=2))

    get_std = staticmethod(get_std)
    get_thumb = staticmethod(get_thumb)
    get_car_std = staticmethod(get_car_std)
    get_car_thumb = staticmethod(get_car_thumb)
    get_cap = staticmethod(get_cap)
    get_pic = staticmethod(get_pic)
    get_user = staticmethod(get_user)

    def get_cache(self):
        if self.cache:
            return self._usercache / str(now())
        return None

    def onlogin_callback(self, cookie, new_settings_file=None):
        'saves cookies upon successful login'
        cache_settings = cookie.settings
        # return self.save_setting(cache_settings, new_settings_file)
        self.cookie = cache_settings

    @staticmethod
    def save_setting(settings, new_settings_file):
        # print(new_settings_file)
        with open(new_settings_file, 'w') as outfile:
            json.dump(settings, outfile, default=to_json)
            _logger.debug('SAVED: {0!s}'.format(new_settings_file))

    @staticmethod
    def load_setting(settings_file, filter_key=None):
        with open(settings_file, 'r') as file_data:
            settings = json.load(file_data, object_hook=from_json)
            if filter_key and isinstance(settings, list):
                settings = list(filter(filter_key, settings))
            _logger.debug('LOADED: {0!s}'.format(settings_file))
        return settings

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value
        if self._debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)

