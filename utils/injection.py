import itertools
from _sims4_collections import frozendict
import functools
import inspect
from functools import wraps
from event_testing.tests import TestList, CompoundTestList
from lot51_core.utils.collections import AttributeDict
from lot51_core.utils.tunables import create_factory_wrapper
from services import get_instance_manager
from lot51_core import logger
from sims4.collections import _ImmutableSlotsBase
from sims4.utils import blueprintmethod, blueprintproperty
from singletons import DEFAULT
from snippets import _TunableAffordanceFilter
from tag import Tag

DEFAULT_SA_KEY = '_super_affordances'
DEFAULT_PHONE_SA_KEY = '_phone_affordances'


def clone_immutable_slots(target, **overrides):
    """
    A helper function to clone an immutable slots object with overrides.

    :param target: original immutable slots
    :param overrides: key/values of items to override
    :return: new immutable slots object
    """
    return target.clone_with_overrides(**overrides)


def merge_dict(original_dict, force_frozen=False, new_items=None, **other_new_items):
    """
    Merges a dict/frozendict/immutableslots, automatically detecting and maintaining type.
    Pass items as kwargs or pass a dict to new_items. If your dict has keys that are not strings you
    cannot spread it using **.

    :param original_dict:
    :param force_frozen: Force a regular dict to return as a frozendict
    :param new_items:
    :param other_new_items:
    :return:
    """
    if new_items is None:
        new_items = dict()
    if isinstance(original_dict, _ImmutableSlotsBase):
        return clone_immutable_slots(original_dict, **new_items, **other_new_items)
    new_dict = dict(original_dict)
    for key, value in itertools.chain(new_items.items(), other_new_items.items()):
        new_dict[key] = value
    if force_frozen or type(original_dict) == frozendict:
        new_dict = frozendict(new_dict)
    return new_dict


def inject_dict(owner, key, force_frozen=False, new_items=None, **other_new_items):
    """
    Merges key/values to a dict/frozendict/immutableslots and injects it back
    onto the owning object.

    :param owner:
    :param key:
    :param force_frozen:
    :param new_items:
    :param other_new_items:
    :return:
    """
    if new_items is None:
        new_items = dict()
    original_dict = getattr(owner, key, dict())
    new_dict = merge_dict(original_dict, force_frozen=force_frozen, new_items=new_items, **other_new_items)
    setattr(owner, key, new_dict)


def inject_tuned_values(owner, **tuned_value_overrides):
    """
    Merges keys/properties to the _tuned_values immutable slots of an
    object and injects it back onto the owning object.

    :param owner:
    :param tuned_value_overrides:
    :return:
    """
    tuned_values = getattr(owner, '_tuned_values')
    new_tuned_values = clone_immutable_slots(tuned_values, **tuned_value_overrides)
    setattr(owner, '_tuned_values', new_tuned_values)


def get_tuned_value(owner, tuned_value_key, default=None):
    """
    Returns an item from _tuned_values by key on the owner, optionally returns a default
    if the key is not found, otherwise None.

    :param owner: The object with _tuned_values
    :param tuned_value_key: The key to get
    :param default: An optional default value to return if the key does not exist
    :return: tuned value property, default, or None
    """
    return getattr(owner._tuned_values, tuned_value_key, default)


def merge_list(original_list, new_items, prepend=False, list_type=None, unique_entries=True):
    """
    Merges a list/tuple/set of items with new items returning a new object. The returned iterable
    will maintain the type of the original_list param unless overridden with the list_type kwarg.
    """
    if list_type is None:
        original_list_type = type(original_list)
        # Check if the original list is None and use the new_items type instead
        if original_list_type == type(None):
            list_type = type(new_items)
        # Use the original_list type as the final list type
        else:
            list_type = type(original_list)

    build_list = list(original_list if original_list is not None else ())
    pix = 0
    for item in new_items:
        if not unique_entries or (unique_entries and item not in build_list):
            if prepend:
                build_list.insert(pix, item)
                pix += 1
            else:
                build_list.append(item)

    return list_type(build_list)


def inject_list(owner, key, new_items, prepend=False, debug=False, safe=True, unique_entries=True):
    """
    Inject new items to an existing list, tuple, set, frozenset.

    Creates a copy of the original list, appends new items to the list,
    then injects the list back onto the owning object.

    :param owner: The object that has the list to inject to.
    :param key: The key on the owner to get the original list
    :param new_items: The new items to add to the list. This can be any iter type
    :param prepend: If True, the new items will be prepended to the list
    :param debug: If True, details of the injection will be logged to lot51_core.log
    :param safe: If True, the injection will not affect objects that do not have the existing key
    :return: None
    """
    if safe and not hasattr(owner, key):
        raise KeyError("Object {} does not have key {}".format(owner, key))

    if new_items is None or not len(new_items):
        if debug:
            logger.info("Injecting List • Owner: {}, Key: {}, No items to add".format(owner, key))
        return

    # Get original list
    original_list = getattr(owner, key, None)
    # Perform merge
    new_list = merge_list(original_list, new_items, prepend=prepend, unique_entries=unique_entries)

    if debug:
        logger.info("Injecting List • Owner: {}, Key: {}, Original List: {}, Final List: {}".format(owner, key, original_list, new_list))

    setattr(owner, key, new_list)


def merge_mapping_lists(owner_map, user_map, prepend=False, list_type=None, unique_entries=True):
    """
    Merges an existing dict of `list_type` into a frozendict that was generated by a TunableMapping.

    :param owner_map:
    :param user_map:
    :param prepend:
    :param list_type:
    :return: new mapping frozendict
    """
    new_mapping = dict(owner_map)
    for k, v in user_map.items():
        if k in new_mapping:
            new_mapping[k] = merge_list(new_mapping[k], v, prepend=prepend, list_type=list_type, unique_entries=unique_entries)
        else:
            new_mapping[k] = merge_list(v, (), list_type=list_type)
    return frozendict(new_mapping)


def inject_mapping_lists(owner, key, user_map, prepend=False, safe=True, debug=False, list_type=None):
    """
    Merges an existing dict of `list_type` into a frozendict that was generated by a TunableMapping
    then injects it back onto the owning object.

    :param owner: The object that has the map
    :param key: The key of the map
    :param user_map: Your dict that should be merged into the owner's map
    :param prepend: Set to True if items should be added to the beginning of the lists
    :param safe: Injection will not be added to owner if the key does not exist and a KeyError will be raised
    :param list_type: Override the list type inferred from the original mapping.
    :return: None
    """
    if safe and not hasattr(owner, key):
        raise KeyError("Object {} does not have key {}".format(owner, key))

    if debug:
        logger.info("Injecting Mapping List • Owner: {}, Key: {}, No items to add".format(owner, key))

    owner_map = dict(getattr(owner, key, {}))
    final_value = merge_mapping_lists(owner_map, user_map, prepend=prepend, list_type=list_type)

    if debug:
        logger.info("Injecting Mapping List • Owner: {}, Key: {}, Original Map: {}, Final Map: {}".format(owner, key, owner_map, final_value))

    setattr(owner, key, final_value)


def merge_affordance_filter(tunable, other_filter=None, include_all_by_default=DEFAULT, include_affordances=(), exclude_affordances=(), include_lists=(), exclude_lists=(), debug=False):
    """
    Merge affordances and affordance lists into an Affordance Compatibility tunable and return a new instance.

    :param tunable: The original affordance filter object
    :param include_affordances: A list of affordances to add to include_affordances
    :param exclude_affordances: A list of affordances to add to exclude_affordances
    :param include_lists: A list of affordance lists to add to include_lists
    :param exclude_lists:  A list of affordance lists to add to exclude_lists
    :return: new affordance filter tunable wrapper
    """
    default_inclusion = tunable.default_inclusion
    overrides = AttributeDict()
    if other_filter is not None:
        other_inclusion = other_filter.default_inclusion
        overrides.include_affordances = merge_list(overrides.include_affordances, other_inclusion.include_affordances)
        overrides.exclude_affordances = merge_list(overrides.exclude_affordances, other_inclusion.exclude_affordances)
        overrides.include_lists = merge_list(overrides.include_lists, other_inclusion.include_lists)
        overrides.exclude_lists = merge_list(overrides.exclude_lists, other_inclusion.exclude_lists)
        overrides.include_all_by_default = other_inclusion.include_all_by_default

    overrides.include_affordances = merge_list(default_inclusion.include_affordances, include_affordances)
    overrides.exclude_affordances = merge_list(default_inclusion.exclude_affordances, exclude_affordances)
    overrides.include_lists = merge_list(default_inclusion.include_lists, include_lists)
    overrides.exclude_lists = merge_list(default_inclusion.exclude_lists, exclude_lists)
    if include_all_by_default is not DEFAULT:
        overrides.include_all_by_default = include_all_by_default

    new_default_inclusion = merge_dict(default_inclusion, new_items=overrides)
    return create_factory_wrapper(_TunableAffordanceFilter, default_inclusion=new_default_inclusion)


def inject_affordance_filter(owner, key, other_filter=None, include_all_by_default=DEFAULT, include_affordances=(), exclude_affordances=(), include_lists=(), exclude_lists=(), debug=False):
    """
    Merge affordances and affordance lists into an Affordance Compatibility tunable and injects it
    back onto the owning object.

    :param tunable: The original affordance filter object
    :param include_affordances: A list of affordances to add to include_affordances
    :param exclude_affordances: A list of affordances to add to exclude_affordances
    :param include_lists: A list of affordance lists to add to include_lists
    :param exclude_lists:  A list of affordance lists to add to exclude_lists
    :return: None
    """
    tunable = getattr(owner, key)
    new_tunable = merge_affordance_filter(
        tunable,
        other_filter=other_filter,
        include_all_by_default=include_all_by_default,
        include_affordances=include_affordances,
        exclude_affordances=exclude_affordances,
        include_lists=include_lists,
        exclude_lists=exclude_lists,
        debug=debug,
    )
    setattr(owner, key, new_tunable)


def clone_test_set(original_tests, additional_and=(), additional_or=(), prepend_and=False, add_if_empty_list=True):
    """
    This function will clone a TunableTestSet/TunableGlobalTestSet and add additional tests,
    returning an object that can safely replace

    :param original_tests: A TestList, CompoundTestList, or tuple of tests.
    :param additional_and: A tuple of tests that will be appended to each test list.
    :param additional_or: A tuple of tests that will be appended to the CompoundTestList.
    :param prepend_and: If True, the additional_and tests will be prepended instead of appended.
    :param add_if_empty_list: if the injection target is a CompoundTestList and is empty, then a new TestList will be
        created with additional_and tests.
    :return: A TestList, CompoundTestList, or tuple of tests matching the `original_tests` param.
    """
    # Represents a TestList returned from a TunableGlobalTestSet
    if isinstance(original_tests, TestList):
        new_tests = TestList(original_tests)
        pix = 0
        for test in additional_and:
            if prepend_and:
                new_tests.insert(test, pix)
                pix += 1
            else:
                new_tests.append(test)
        return new_tests
    # Represents a CompoundTestList returned from a TunableTestSet
    elif isinstance(original_tests, CompoundTestList):
        new_compound = CompoundTestList()

        if not len(original_tests) and add_if_empty_list:
            # Add nested test list if empty
            new_tests = clone_test_set(TestList(), additional_and=additional_and)
            new_compound.append(new_tests)
        else:
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
        pix = 0
        for test in additional_and:
            if prepend_and:
                new_tests.insert(test, pix)
                pix += 1
            else:
                new_tests.append(test)
        return tuple(new_tests)


def obj_has_affordance(obj, affordance, key=DEFAULT_SA_KEY):
    if not hasattr(obj, key):
        return False
    return affordance in getattr(obj, key)


def add_affordance(obj, interaction=None, key=DEFAULT_SA_KEY):
    if interaction is not None:
        inject_list(obj, key, (interaction,), debug=False,)


def add_affordances(obj, interactions=tuple(), key=DEFAULT_SA_KEY):
    inject_list(obj, key, interactions, debug=False,)


def add_phone_affordances(obj, interactions=tuple(), key=DEFAULT_PHONE_SA_KEY):
    inject_list(obj, key, interactions, debug=False,)


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
        elif type(target_function) is staticmethod:
            return staticmethod(_wrapped_func)
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
