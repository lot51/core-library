import build_buy
from sims4.service_manager import Service
from lot51_core.services.events import event_service, CoreEvent
from lot51_core.services.service_manager import service_manager
from lot51_core.utils.context import Context


class GlobalService(Service):

    def save(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.GAME_SAVE, context=context, **kwargs)

    def pre_save(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.GAME_PRE_SAVE, context=context, **kwargs)

    def setup(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.GAME_SETUP, context=context, **kwargs)

    def load(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.GAME_LOAD, context=context, **kwargs)

    def start(self, *args, **kwargs):
        build_buy.register_build_buy_enter_callback(self.on_build_buy_enter)
        build_buy.register_build_buy_exit_callback(self.on_build_buy_exit)
        event_service.process_event(CoreEvent.GLOBAL_SERVICE_START)

    def stop(self, *args, **kwargs):
        build_buy.unregister_build_buy_enter_callback(self.on_build_buy_enter)
        build_buy.unregister_build_buy_exit_callback(self.on_build_buy_exit)
        event_service.process_event(CoreEvent.GLOBAL_SERVICE_STOP)

    def on_zone_load(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.ZONE_LOAD, context=context)

    def on_zone_unload(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.ZONE_UNLOAD, context=context)

    def on_cleanup_zone_objects(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.ZONE_CLEANUP_OBJECTS, context=context)

    def on_all_households_and_sim_infos_loaded(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.HOUSEHOLDS_AND_SIMS_LOADED, context=context)

    def on_build_buy_enter(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.BUILD_BUY_ENTER, context=context)

    def on_build_buy_exit(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event(CoreEvent.BUILD_BUY_EXIT, context=context)


service_manager.register_service(GlobalService)
