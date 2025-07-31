from lot51_core.utils.emitter import EventEmitter
from lot51_core import logger as lot51_core_logger
import sims4


class CoreEvent:
    CLIENT_CONNECT = 'client.connect'
    CLIENT_DISCONNECT = 'client.disconnect'
    BUILD_BUY_ENTER = 'build_buy.enter'
    BUILD_BUY_EXIT = 'build_buy.exit'
    BUILD_BUY_FIXUP = 'build_buy.fixup'
    GAME_SETUP = 'game.setup'
    GAME_LOAD = 'game.load'
    GAME_PRE_SAVE = 'game.pre_save'
    GAME_SAVE = 'game.save'
    GAME_SERVICES_STARTED = 'game_services.started'
    GAME_TICK = 'game.update'
    GLOBAL_SERVICE_START = 'global_service.start'
    GLOBAL_SERVICE_STOP = 'global_service.stop'
    HOUSEHOLDS_AND_SIMS_LOADED = 'zone.all_households_and_sim_infos_loaded'
    LOADING_SCREEN_LIFTED = 'zone.loading_screen_lifted'
    TUNING_LOADED = 'instance_managers.loaded'
    ZONE_CLEANUP_OBJECTS = 'zone.cleanup_objects'
    ZONE_LOAD = 'zone.load'
    ZONE_UNLOAD = 'zone.unload'
    LOT_CLEARING_BEGIN = 'lot_clearing.begin'
    LOT_CLEARING_END = 'lot_clearing.end'
    OBJECT_ADDED = 'game_object.added'
    OBJECT_DESTROYED = 'game_object.destroyed'


class EventService(EventEmitter):

    def __init__(self, logger=lot51_core_logger):
        super().__init__()
        self.logger = logger

    def handler(self, event_name: str, weight=1):
        def wrapper(func):
            self.add_listener(event_name, func, weight=weight)
            return func
        return wrapper

    def process_event(self, event_name: str, *args, **kwargs):
        for (listener_name, callback, weight) in self.get_ordered_listeners():
            if listener_name != event_name:
                continue
            try:
                callback(self, *args, **kwargs)
            except:
                self.logger.exception("[EventService] failed processing event: {}".format(event_name))


event_service = EventService()


def event_handler(event_name: str, weight=1):
    def wrapper(func):
        event_service.add_listener(event_name, func, weight=weight)
        return func
    return wrapper


@sims4.commands.Command('lot51_lib.list_event_listeners', command_type=sims4.commands.CommandType.Live)
def list_event_listeners(_connection=None):
    for (listener_name, callback, weight) in event_service.get_ordered_listeners():
        lot51_core_logger.info("listener: {} {} {}".format(listener_name, callback, weight,))
