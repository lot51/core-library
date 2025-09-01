from services import get_instance_manager
from sims4.resources import Types, get_resource_key


def get_resource(tuning_id, resource_type: Types):
    if resource_type is None:
        raise ValueError("Missing resource_type")
    if tuning_id is not None:
        tuning_id = int(tuning_id)
        manager = get_instance_manager(resource_type)
        if manager is not None:
            return manager.types.get(get_resource_key(tuning_id, resource_type))
