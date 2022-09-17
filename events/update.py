from broadcasters.broadcaster_service import BroadcasterService
from lot51_core.utils.injection import inject_to
from lot51_core.utils.context import Context
from lot51_core.services.events import event_service


@inject_to(BroadcasterService, 'update')
def _on_update(original, *args, **kwargs):
    original(*args, **kwargs)
    try:
        context = Context.get_current_context()
        event_service.process_event("game.update", context=context)
    except:
       pass