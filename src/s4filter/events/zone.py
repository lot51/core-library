from lot51_core import logger
from lot51_core.services.events import event_service, CoreEvent
from lot51_core.utils.injection import inject_to
from lot51_core.utils.context import Context
from zone import Zone
from zone_spin_up_service import ZoneSpinUpService


@inject_to(ZoneSpinUpService, 'on_loading_screen_animation_finished')
def _on_loading_screen_animation_finished(original, *args, **kwargs):
    original(*args, **kwargs)
    try:
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.LOADING_SCREEN_LIFTED, context=context)
    except:
        logger.exception("error processing loading screen lifted")


@inject_to(Zone, 'on_active_lot_clearing_begin')
def _on_active_lot_clearing_begin(original, *args, **kwargs):
    original(*args, **kwargs)
    try:
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.LOT_CLEARING_BEGIN, context=context)
    except:
        logger.exception("error processing lot clearing begin")


@inject_to(Zone, 'on_active_lot_clearing_end')
def _on_active_lot_clearing_begin(original, *args, **kwargs):
    original(*args, **kwargs)
    try:
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.LOT_CLEARING_END, context=context)
    except:
        logger.exception("error processing lot clearing end")


@inject_to(Zone, '_add_expenditures_and_do_post_bb_fixup')
def _on_build_buy_fixup(original, self, *args, **kwargs):
    try:
        objects_to_fixup = tuple(self.objects_to_fixup_post_bb) if self.objects_to_fixup_post_bb is not None else ()
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.BUILD_BUY_FIXUP, context=context, objects_to_fixup=objects_to_fixup)
    except:
        logger.exception("error processing build buy fixup")

    original(self, *args, **kwargs)