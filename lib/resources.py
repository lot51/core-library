from services import get_instance_manager
from sims4.resources import Types


def get_resource(tuning_id, resource_type: Types):
    if tuning_id is not None:
        tuning_id = int(tuning_id)
        manager = get_instance_manager(resource_type)
        if manager is not None:
            return manager.get(tuning_id)