import functools
import inspect
from functools import wraps
from event_testing.tests import TestList, CompoundTestList
from services import get_instance_manager
from lot51_core import logger
from sims4.utils import blueprintmethod, blueprintproperty
from tag import Tag

DEFAULT_SA_KEY = '_super_affordances'
DEFAULT_PHONE_SA_KEY = '_phone_affordances'


def clone_test_set(original_tests, additional_and=(), additional_or=(), prepend_and=False):
    """
    This function will clone a TunableTestSet/TunableGlobalTestSet and add additional tests,
    returning an object that can safely replace

    :param original_tests: A TestList, CompoundTestList, or tuple of tests.
    :param additional_and: A tuple of tests that will be appended to each test list.
    :param additional_or: A tuple of tests that will be appended to the CompoundTestList.
    :param prepend_and: If True, the additional_and tests will be prepended instead of appended.
    :return: A TestList, CompoundTestList, or tuple of tests matching the `original_tests` param.
    """
    # Represents a TestList returned from a TunableGlobalTestSet
    if isinstance(original_tests, TestList):
        new_tests = TestList(original_tests)
        for test in additional_and:
            if prepend_and:
                new_tests.insert(test, 0)
            else:
                new_tests.append(test)
        return new_tests
    # Represents a CompoundTestList returned from a TunableTestSet
    elif isinstance(original_tests, CompoundTestList):
        new_compound = CompoundTestList()
        # Clone nested test lists with additional AND tests appended
        for test_list in original_tests:
            new_tests = clone_test_set(test_list, additional_and=additional_and)
            new_compound.append(new_tests)
        # Add additional OR tests
        for test_list in additional_or:
            new_compound.append(test_list)
        return new_compound
    # Represents a tuple of tests that are within a CompoundTestList
    else:
        # Clone the tuple and append additional AND tests
        new_tests = list(original_tests)
        for test in additional_and:
            if prepend_and:
                new_tests.insert(test, 0)
            else:
                new_tests.append(test)
        return tuple(new_tests)


def obj_has_affordance(obj, affordance, key=DEFAULT_SA_KEY):
    if not hasattr(obj, key):
        return False
    return affordance in getattr(obj, key)


def add_affordance(obj, interaction=None, key=DEFAULT_SA_KEY):
    if interaction and hasattr(obj, key) and not obj_has_affordance(obj, interaction, key):
        if isinstance(getattr(obj, key), frozenset):
            setattr(obj, key, frozenset(set(getattr(obj, key)).union({interaction})))
        elif isinstance(getattr(obj, key), set):
            setattr(obj, key, set(getattr(obj, key)).union({interaction}))
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
    """
    Tests if a function is decorated with @flexmethod by checking if it was wrapped with functools.partial,
    and inspects the name of the first 2 arguments to see if they use "cls" and "inst". This is not guaranteed, but
    is a common pattern EA uses.

    :param target_function: The function to test
    :return: bool
    """
    if type(target_function) is functools.partial:
        spec = inspect.getfullargspec(target_function.func)
        return len(spec.args) >= 2 and spec.args[0] == 'cls' and spec.args[1] == 'inst'
    return False


def inject_to(target_object, target_function_name, force_flex=False, force_untuned_cls=False):
    """
    Decorator to inject a function into an existing function. The original function will be provided as the first
    argument in your decorated function, with the original args/kwargs following. Depending on your goals, you should
    call the original function and pass the args/kwargs. Return the original result if necessary.

    Based on TURBODRIVER's Injector
    https://turbodriver-sims.medium.com/basic-python-injecting-into-the-sims-4-cdc85a741b10

    :param target_object: The class or instance to inject to
    :param target_function_name: The name of the function to replace on the target_object
    :param force_flex: Set to True if the target function is a flex method but does not use "cls" and "inst" as names of the first 2 arguments.
    :param force_untuned_cls: Set to True to retrieve the raw untuned class as the "cls" argument in a class method.
        As of 1.16 class methods will now provide the tuned class as "cls". This property was added to return the original default functionality.
    """

    def _wrap_target(target_function, new_function):
        @wraps(target_function)
        def _wrapped_func(*args, **kwargs):
            if type(target_function) is blueprintmethod:
                return new_function(target_function.func, *args, **kwargs)
            elif type(target_function) is blueprintproperty or type(target_function) is property:
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

        if type(target_function) is blueprintmethod:
            return blueprintmethod(_wrapped_func)
        elif type(target_function) is blueprintproperty:
            return blueprintproperty(_wrapped_func)
        elif inspect.ismethod(target_function):
            if hasattr(target_function, '__self__') and force_untuned_cls:
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
