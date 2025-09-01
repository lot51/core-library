import sys
from urllib.parse import urlencode


def is_system64():
    return sys.maxsize > 2**32


def is_system32():
    return not is_system64()


def is_windows():
    return sys.platform in ('win32', 'cygwin',)


def is_mac():
    return sys.platform == 'darwin'


def is_linux():
    return sys.platform in ('linux', 'linux2',)


def open_url_in_browser(url, **query):
    try:
        import webbrowser
        if query is not None:
            params = urlencode(query)
            full_url = "{}?{}".format(url, params)
        else:
            full_url = url
        webbrowser.open(full_url)
        return True
    except:
        return False
