from lot51_core.utils.injection import inject_to
from lot51_core.services.events import event_service
from objects.game_object import GameObject


@inject_to(GameObject, 'on_add')
def _on_update(original, self, *args, **kwargs):
    original(*args, self, **kwargs)
    try:
        event_service.process_event("game_object.added", self)
    except:
       pass


@inject_to(GameObject, 'on_remove')
def _on_update(original, self, *args, **kwargs):
    try:
        event_service.process_event("game_object.destroyed", self)
    except:
       pass

    original(*args, self, **kwargs)