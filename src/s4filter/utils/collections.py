# https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
class AttributeDict(dict):
    """dot.notation access to dictionary attributes"""
    def __getattr__(self, attr):
        # https://github.com/aparo/pyes/issues/183#issuecomment-5818783
        # raise attr error to avoid typeerror when pickling
        if attr.startswith('__'):
            raise AttributeError
        return self.get(attr, None)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def dict2attr(old_dict: dict):
    """
    Recursively converts a default dict object to an AttributeDict

    :param old_dict: dict
    :return: AttributeDict
    """
    new_dict = AttributeDict(old_dict)
    for key, value in new_dict.items():
        if isinstance(value, dict):
            new_dict[key] = dict2attr(value)
    return new_dict


def kw2dict(**kwargs):
    """
    Converts keyword args to AttributeDict

    :param kwargs:
    :return: AttributeDict
    """
    return dict2attr(kwargs)