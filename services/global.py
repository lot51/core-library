import build_buy
from sims4.service_manager import Service
from lot51_core.services.events import event_service
from lot51_core.services.service_manager import service_manager
from lot51_core.utils.context import Context


class GlobalService(Service):

    def save(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event("game.save", context=context, **kwargs)

    def pre_save(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event("game.pre_save", context=context, **kwargs)

    def setup(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event("game.setup", context=context, **kwargs)

    def load(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event("game.load", context=context, **kwargs)

    def start(self, *args, **kwargs):
        build_buy.register_build_buy_enter_callback(self.on_build_buy_enter)
        build_buy.register_build_buy_exit_callback(self.on_build_buy_exit)
        event_service.process_event("global_service.start")

    def stop(self, *args, **kwargs):
        build_buy.unregister_build_buy_enter_callback(self.on_build_buy_enter)
        build_buy.unregister_build_buy_exit_callback(self.on_build_buy_exit)
        event_service.process_event("global_service.stop")

    def on_zone_load(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event("zone.load", context=context)

    def on_zone_unload(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event("zone.unload", context=context)

    def on_cleanup_zone_objects(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event("zone.cleanup_objects", context=context)

    def on_all_households_and_sim_infos_loaded(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event("zone.all_households_and_sim_infos_loaded", context=context)

    def on_build_buy_enter(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event("build_buy.enter", context=context)

    def on_build_buy_exit(self, *args, **kwargs):
        context = Context.get_current_context()
        event_service.process_event("build_buy.exit", context=context)


service_manager.register_service(GlobalService)
