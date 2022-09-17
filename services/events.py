from lot51_core.utils.emitter import EventEmitter
from lot51_core import logger
import sims4


class EventService(EventEmitter):

    def __init__(self):
        super().__init__()

    def process_event(self, event_name: str, *args, **kwargs):
        for (listener_name, callback) in self._listeners:
            if listener_name != event_name:
                continue
            try:
                # logger.debug("[callback] {} {}".format(event_name, callback))
                callback(self, *args, **kwargs)
            except:
                logger.exception("[EventService] failed processing event: {}".format(event_name))


event_service = EventService()


def event_handler(event_name: str):
    def wrapper(func):
        event_service.add_listener(event_name, func)
        return func
    return wrapper


@sims4.commands.Command('lot51_lib.list_event_listeners', command_type=sims4.commands.CommandType.Live)
def list_event_listeners(_connection=None):
    for (listener_name, callback) in event_service._listeners:
        logger.debug("listener: {} {}".format(listener_name, callback))
