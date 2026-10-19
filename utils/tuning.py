import services
from sims4.resources import Types
from sims4.tuning.instances import create_tuning_blueprint_class


_ordered_snippets_cache = dict()


def create_tuning_blueprint(base_class, name):
    tuning_blueprint_cls = create_tuning_blueprint_class(base_class)
    tuning_blueprint = tuning_blueprint_cls(name)
    return tuning_blueprint


def get_ordered_snippets(only_subclasses_of):
    """
    Returns the snippets that are subclasses of `only_subclasses_of`, in the same order as
    InstanceManager.get_ordered_types.

    get_ordered_types scans every snippet in the game on each call, so the result is cached once
    the snippet manager has finished loading. The cache is rebuilt if the number of snippets changes,
    and cleared when packs are hot loaded.
    """
    manager = services.get_instance_manager(Types.SNIPPET)
    if not manager.all_instances_loaded:
        return tuple(manager.get_ordered_types(only_subclasses_of=only_subclasses_of))
    count = len(manager.types)
    cached = _ordered_snippets_cache.get(only_subclasses_of)
    if cached is None or cached[0] != count:
        cached = (count, tuple(manager.get_ordered_types(only_subclasses_of=only_subclasses_of)))
        _ordered_snippets_cache[only_subclasses_of] = cached
    return cached[1]


def clear_ordered_snippets_cache():
    _ordered_snippets_cache.clear()