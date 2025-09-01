from lot51_core.utils.injection import inject_to
from lot51_core.services.events import event_service, CoreEvent
from objects.game_object import GameObject


@inject_to(GameObject, 'on_add')
def _on_game_object_add(original, self, *args, **kwargs):
    original(self, *args, **kwargs)
    try:
        event_service.process_event(CoreEvent.OBJECT_ADDED, self)
    except:
       pass


@inject_to(GameObject, 'on_remove')
def _on_game_object_remove(original, self, *args, **kwargs):
    try:
        event_service.process_event(CoreEvent.OBJECT_DESTROYED, self)
    except:
       pass

    original(*args, self, **kwargs)