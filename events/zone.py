from lot51_core import logger
from lot51_core.services.events import event_service, CoreEvent
from lot51_core.utils.injection import inject_to
from lot51_core.utils.context import Context
from zone_spin_up_service import ZoneSpinUpService


@inject_to(ZoneSpinUpService, 'on_loading_screen_animation_finished')
def _on_loading_screen_animation_finished(original, *args, **kwargs):
    original(*args, **kwargs)
    try:
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.LOADING_SCREEN_LIFTED, context=context)
    except:
        logger.exception("error processing loading screen lifted")