from lot51_core import logger
from typing import AnyStr, Callable


class EventEmitter:

    def __init__(self):
        self._listeners = list()

    def _on_event_processed(self, event_name: str, result=None, event_args=None, event_kwargs=None):
        pass

    def process_event(self, event_name: str, *args, **kwargs):
        for (listener_name, callback) in self._listeners:
            if listener_name != event_name:
                continue
            try:
                result = callback(*args, **kwargs)
                self._on_event_processed(event_name, result=result, event_args=args, event_kwargs=kwargs)
            except:
                logger.exception("Failed processing event")

    def add_listener(self, event_name: AnyStr, callback: Callable):
        self._listeners.append((event_name, callback,))

    def remove_listener(self, event_name: AnyStr, callback: Callable):
        self._listeners.remove((event_name, callback,))
