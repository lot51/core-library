import functools
import inspect
from functools import wraps
from services import get_instance_manager
from lot51_core import logger
from tag import Tag

DEFAULT_SA_KEY = '_super_affordances'
DEFAULT_PHONE_SA_KEY = '_phone_affordances'


def obj_has_affordance(obj, affordance, key=DEFAULT_SA_KEY):
    if not hasattr(obj, key):
        return False
    return affordance in getattr(obj, key)


def add_affordance(obj, interaction=None, key=DEFAULT_SA_KEY):
    if interaction and hasattr(obj, key) and not obj_has_affordance(obj, interaction, key):
        if isinstance(getattr(obj, key), set):
            setattr(obj, key, set(getattr(obj, key)).union({interaction}))
        if isinstance(getattr(obj, key), frozenset):
            setattr(obj, key, frozenset(set(getattr(obj, key)).union({interaction})))
        else:
            setattr(obj, key, getattr(obj, key) + (interaction,))


def add_affordances(obj, interactions=tuple(), key=DEFAULT_SA_KEY):
    if interactions and hasattr(obj, key):
        for interaction in interactions:
            add_affordance(obj, interaction, key)


def add_phone_affordances(obj, interactions=tuple(), key=DEFAULT_PHONE_SA_KEY):
    add_affordances(obj, interactions, key)


def add_phone_affordance(obj, interaction=None, key=DEFAULT_PHONE_SA_KEY):
    add_affordance(obj, interaction, key)


def add_tags(tags):
    inject_to_enum(tags, Tag)


def inject_to_enum(kvp, enum_class):
    with enum_class.make_mutable():
        for (k, v) in kvp.items():
            enum_class._add_new_enum_value(k, v)


def is_flexmethod(target_function):
    if type(target_function) is functools.partial:
        spec = inspect.getfullargspec(target_function.func)
        return len(spec.args) >= 2 and spec.args[0] == 'cls' and spec.args[1] == 'inst'
    return False


# Injection decorator based on TURBODRIVER's injector
# https://turbodriver-sims.medium.com/basic-python-injecting-into-the-sims-4-cdc85a741b10
def inject_to(target_object, target_function_name, force_flex=False):

    def _wrap_target(target_function, new_function):
        @wraps(target_function)
        def _wrapped_func(*args, **kwargs):
            if type(target_function) is property:
                return new_function(target_function.fget, *args, **kwargs)
            elif force_flex or is_flexmethod(target_function):
                def new_flex_function(original, *nargs, **nkwargs):
                    cls = original.args[0]
                    inst = next(iter(narg for narg in nargs if type(narg) is cls), None)
                    if inst is not None:
                        nargs = list(nargs)
                        nargs.remove(inst)
                    return new_function(original.func, cls, inst, *nargs, **nkwargs)
                return new_flex_function(target_function, *args, **kwargs)
            return new_function(target_function, *args, **kwargs)

        if inspect.ismethod(target_function):
            if hasattr(target_function, '__self__'):
                return _wrapped_func.__get__(target_function.__self__, target_function.__self__.__class__)
            return classmethod(_wrapped_func)
        elif type(target_function) is property:
            return property(_wrapped_func)
        return _wrapped_func

    def _inject(new_function):
        target_function = getattr(target_object, target_function_name)
        setattr(target_object, target_function_name, _wrap_target(target_function, new_function))
        return new_function

    return _inject


# Tuning manager decorator to run code when the manager has loaded all tuning.
# Created by Frank: https://frankkmods.com
def on_load_complete(manager_type):
    def wrapper(function):
        def safe_function(manager, *_, **__):
            try:
                function(manager)
            except Exception as e:
                logger.exception("failed to load manager: {}".format(manager_type))
        get_instance_manager(manager_type).add_on_load_complete(safe_function)
    return wrapper
