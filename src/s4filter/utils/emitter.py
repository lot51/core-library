from lot51_core import logger
from typing import AnyStr, Callable


class EventEmitter:

    def __init__(self):
        self._listeners = list()

    def _on_event_processed(self, event_name: str, result=None, event_args=None, event_kwargs=None):
        pass

    def get_ordered_listeners(self):
        return sorted(self._listeners, key=lambda item: item[2])

    def process_event(self, event_name: str, *args, **kwargs):
        for (listener_name, callback, weight) in self.get_ordered_listeners():
            if listener_name != event_name:
                continue
            try:
                result = callback(*args, **kwargs)
                self._on_event_processed(event_name, result=result, event_args=args, event_kwargs=kwargs)
            except:
                logger.exception("Failed processing event")

    def add_listener(self, event_name: AnyStr, callback: Callable, weight=1):
        self._listeners.append((event_name, callback, weight,))

    def remove_listener(self, event_name: AnyStr, callback: Callable, weight=1):
        self._listeners.remove((event_name, callback, weight,))
