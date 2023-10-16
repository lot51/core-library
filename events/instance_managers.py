from lot51_core.services.events import event_service, CoreEvent
from lot51_core.utils.injection import on_load_complete
from sims4.resources import Types


@on_load_complete(Types.TDESC_DEBUG)
def _on_instance_managers_loaded(*args):
    try:
        event_service.process_event(CoreEvent.TUNING_LOADED)
    except:
        pass
