from __future__ import print_function, division

import atexit

'''
@changelist:
2.1: added internal file objects along with functionalities to handle and check open/close state of file.
2.2: support for tty files.
2.3: support path and parent resolution, traversing, file comparison
2.4: add breakpoint, socks_proxy_installer
'''

__author__ = 'Mohammad Kajbaf'
__version__ = '2.4'


import sys
from os.path import isfile, isdir, exists, join, abspath, realpath, pardir, dirname, expanduser, expandvars, getatime, getmtime, getctime, getsize, islink, ismount, samefile, sameopenfile, basename, dirname
from os import makedirs, rmdir, unlink, symlink, link
import os, os.path, io
try:
    from os import PathLike
except ImportError:
    PathLike = object
file_type = getattr(__builtins__, 'file', io.IOBase)
inp = getattr(__builtins__, 'raw_input', input)


def automain(func):
    """decorator to declare the _main_ function which will be default to run
    use as:
    @automain
    def default_func():
    ...pass"""
    import inspect
    parent = inspect.stack()[1][0]
    name = parent.f_locals.get('__name__', None)
    if name == '__main__':
        func()


def info(*objs):
    """function to write information messages to stdout"""
    print('INFO ', *objs, file=sys.stdout)


def warning(*objs):
    """function to write warning messages to stderr"""
    print('WARNING ', *objs, file=sys.stderr)


def error(*objs):
    """function to write error messages to stderr"""
    print('ERROR ', *objs, file=sys.stderr)


def getint(message):
    """function to get integer from input"""
    try:
        i = int(inp(message))
    except ValueError as e:
        warning(e)
        raise e
    return i


def getfloat(message):
    """function to get float from input"""
    try:
        f = float(inp(message))
    except ValueError as e:
        warning(e)
        raise e
    return f


def getstr(message):
    """function to get string from input"""
    try:
        str = inp(message)
    except ValueError as e:
        warning(e)
        raise e
    return str


def isdebug():
    """function to check Kaj Debug mode"""
    return globals().get('DEBUG', 0)

def set_debug():
    """function to set Kaj Debug mode"""
    globals()['DEBUG'] = 1

def clear_debug():
    """function to reset Kaj Debug mode"""
    globals()['DEBUG'] = 0

def breakpoint():
    import ipdb
    ipdb.set_trace(context=6)

class path(PathLike):
    r"""
    Instances of this class represent a file path, and facilitate
    several operations on files and directories.
    Its most surprising feature is that it overloads the division
    operator, so that the result of placing a / operator between two
    paths (or between a path and a string) results in a longer path,
    representing the two operands joined by the system's path
    separator character.
    Now, it handles openning and closing of files like a charm!
    """
    def __init__(self, target):
        if isinstance(target, path):
            self.target = target.target
            self.f = target.f
        elif isinstance(target, file_type):
            self.f = file
            self.target = file.name
        else:
            self.target = target
            self.f = None

    def exists(self):
        return exists(self.target)

    def isfile(self):
        return isfile(self.target)

    def isdir(self):
        return isdir(self.target)

    def isopen(self):
        return True if self.f and not self.f.closed else False

    def isatty(self):
        return self.f.isatty()

    def islink(self):
        return islink(self.target)
    
    def ismount(self):
        return ismount(self.target)

    def parent(self):
        if self.isfile():
            return path(dirname(self.abspath()))
        else:
            parent = (self / pardir)
            parent.abspath(persist=True)
            return parent

    def abspath(self, followlinks=False, persist=False):
        _fullpath = realpath(self.target) if followlinks else abspath(self.target)
        if persist:
            self.target = _fullpath
        return _fullpath

    def mklink(self, dest):
        os.symlink(self.abspath(followlinks=True), dest)
        
    def mkdir(self, mode = 493):
        makedirs(self.abspath(), mode)
        
    def listdir(self, recursive=False, files=True, dirs=True, root=False, followlinks=False):
        _dirs = []
        _files = []
        _list = []
        if root:
            _list.append(self)

        for r, d, f in os.walk(self.abspath(followlinks=followlinks), followlinks=followlinks):
            root = path(r)
            if dirs:
                _dirs.extend(
                    [root/x for x in d]
                )
            if files:
                _files.extend(
                    [root/x for x in f]
                )
            if not recursive:
                break
        _list.extend(_dirs)
        _list.extend(_files)
        return _list

    def rmdir(self):
        if self.isdir():
            rmdir(self.target)
        else:
            raise ValueError('Path does not represent a directory')
        
    def getctime(self):
        return getctime(self.target)    
    
    def getatime(self):
        return getatime(self.target)
    
    def getmtime(self):
        return getmtime(self.target)
            
    def getctime(self):
        return getctime(self.target)    
    
    def getsize(self):
        return getsize(self.target)

    def name(self):
        _t = self.target
        if _t.rfind(os.sep, -1) > 0:
           _t = _t[:-1]
        return basename(_t)

    def dirname(self):
        _t = self.target
        if _t.rfind(os.sep, -1) > 0:
           _t = _t[:-1]
        return dirname(_t)

    def delete(self):
        if self.isopen():
            self.close()
        if self.isfile():
            unlink(self.target)
        else:
            raise ValueError('Path does not represent a file')

    def open(self, mode = "r"):
        if self.isopen():
            if self._mode == mode or self.isatty():
                return self.f
            else:
                self.close()
        self._mode = mode
        self.f = open(self.target, mode)
        return self.f

    def close(self):
        if self.isopen() and not self.isatty():
            self.f.close()

    @staticmethod
    def join(path, fname):
        return join(path, fname)
    
    @staticmethod               
    def expanduser(target):      
        return expanduser(target)

    @staticmethod               
    def expandvars(target):      
        return expandvars(target)

    @staticmethod               
    def pwd():      
        return os.getcwd()

    def __div__(self, other):
        if isinstance(other, path):
            return path(join(self.target, other.target))
        return path(join(self.target, other))
    __truediv__ = __div__

    def __fspath__(self):
        return self.target

    def __repr__(self):
        return '<path %s>' % self.target

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return u'%s' % self.target
    
    def __eq__(self, other):
        if isinstance(other, path):
            return samefile(self.target, other.target)
        return samefile(self.target, other)
    
    def same_stream(self, other):
        if isinstance(other, path):
            return sameopenfile(self.f, other.f)
        return sameopen(self.f, other)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # import ipdb;         ipdb.set_trace()
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
            if hasattr(instance, 'cleanup'):
                atexit.register(instance.cleanup)

        return cls._instances[cls]

def install_socks_proxy_opener(proxytype, proxyaddr='127.0.0.1', proxyport=1080): 
    """ Install a socks proxy handler so that all urllib requests are routed through the socks proxy. """ 
    import urllib 
    try: 
        import socks 
        from sockshandler import SocksiPyHandler 
    except ImportError: 
        warn('WARNING: Failed to load PySocks module. Try installing it with `pip install PySocks`.') 
        return 
    if proxytype == 4: 
        proxytype = socks.SOCKS4 
    elif proxytype == 5: 
        proxytype = socks.SOCKS5 
    else: 
        abort("Unknown Socks Proxy type {0}".format(proxytype)) 
 
    opener = urllib.request.build_opener(SocksiPyHandler(proxytype, proxyaddr, proxyport)) 
    urllib.request.install_opener(opener) 
                                                                                                               
