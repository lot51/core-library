from sims4.tuning.tunable import TunableFactory


def create_factory_wrapper(cls, locked_args=None, **tuned_values):
    """
    Create a tunable factory wrapper from a base class that has a tunable factory, or extends TunableFactory.

    :param cls: The factory class to be wrapped
    :param locked_args: A dict of locked properties on the wrapper, that cant be overidden during call.
    :param tuned_values: Tuned key/values to override in the original wrapper.
    :return: a new wrapper that can be called to generate a tuned instance
    """
    locked_args = locked_args or {}
    if isinstance(cls, type) and issubclass(cls, TunableFactory):
        # this means the cls is a subclass of TunableFactory and can be called directly
        factory = cls(locked_args=locked_args)
    elif hasattr(cls, 'TunableFactory'):
        # this means the cls is a subclass of HasFactoryTunable or HasFactorySingletonTunable
        # and provides the TunableFactory as a property.
        factory = cls.TunableFactory(locked_args=locked_args)
    else:
        # the FACTORY_TYPE on the wrapper was probably overridden with a staticmethod
        # and this will not work for auto-detecting the class to wrap.
        raise ValueError("Unable to detect TunableFactory on cls: {}".format(cls))

    # Get default values for untuned items
    leftovers = set(factory.tunable_items.keys()) - tuned_values.keys()
    for name in leftovers:
        template = factory.tunable_items[name]
        tuplevalue = template.default
        tuned_values[name] = tuplevalue
    return factory._create_dict(tuned_values, factory.locked_args)


def clone_factory_wrapper_with_overrides(wrapper, locked_args=None, **tuned_values_overrides):
    """
    Clones a TunableFactoryWrapper with optional overrides. The wrapped class usually extends HasTunableFactory.

    :param wrapper: The wrapper to clone
    :param locked_args: A dict of locked properties on the wrapper, that cant be overidden during call.
    :param tuned_values_overrides: Tuned key/values to override in the original wrapper.
    :return:
    """
    if not isinstance(wrapper, TunableFactory.TunableFactoryWrapper):
        raise ValueError("`wrapper` is not a TunableFactoryWrapper: {}".format(wrapper))

    cls = wrapper.factory
    if locked_args:
        tuned_values_overrides.update(locked_args)
    tuned_values = wrapper._tuned_values.clone_with_overrides(**tuned_values_overrides)
    return TunableFactory.TunableFactoryWrapper(tuned_values, wrapper._name, cls)


def clone_factory_with_overrides(cls, auto_init=True, locked_args=None, **tuned_values_overrides):
    """
    Clones an instantiated tunable that extends HasTunableSingletonFactory, with optional overrides.
    Turn auto_init off to return a wrapper.

    :param cls: The tunable to clone
    :param auto_init: True by default, calls the TunableFactoryWrapper to return the tuned class. Set to False to return the wrapper.
    :param locked_args:  A dict of locked properties on the wrapper, that cant be overidden during call. Only necessary if auto_init is False.
    :param tuned_values_overrides: Tuned key/values to override in the new wrapper.
    :return: instantiated tunable
    """
    tuned_values = dict(cls.__dict__)
    for key, value in tuned_values_overrides.items():
        tuned_values[key] = value
    factory = cls.TunableFactory(locked_args=locked_args)
    wrapper = factory._create_dict(tuned_values, factory.locked_args)
    if auto_init:
        return wrapper()
    return wrapper
