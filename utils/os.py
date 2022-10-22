from urllib.parse import urlencode


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
