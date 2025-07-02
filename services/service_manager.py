from game_services import GameServiceManager
from lot51_core import logger
from lot51_core.services.events import event_service, CoreEvent
from lot51_core.utils.injection import inject_to
from sims4.service_manager import Service


class ServiceManager:

    def __init__(self):
        self._started = False
        self._services = {}
        self._init_critical_services = {}

    @property
    def started(self):
        return self._started

    @started.setter
    def started(self, val):
        if self._started:
            return
        self._started = val

    def register_service(self, factory, init_critical=False, early_load=False):
        try:
            service = factory()
            if init_critical:
                self._init_critical_services[factory] = (service, early_load,)
            else:
                self._services[factory] = (service, early_load,)
            return service
        except:
            logger.exception("[ServiceManager] failed registering service: {}".format(factory))

    def get_services_gen(self):
        yield from self._services.items()

    def get_critical_services_gen(self):
        yield from self._init_critical_services.items()

    def get_service(self, factory: Service):
        if factory in self._services:
            return self._services[factory][0]
        if factory in self._init_critical_services:
            return self._init_critical_services[factory][0]


service_manager = ServiceManager()


@inject_to(GameServiceManager, 'start_services')
def _start_game_services(original, self, *args, **kwargs):
    try:
        for key, service_tuple in service_manager.get_critical_services_gen():
            try:
                service, early_load = service_tuple
                if early_load:
                    self.services.insert(0, service)
                    self._init_critical_services.insert(0, service)
                else:
                    self.register_service(service, is_init_critical=True)
            except:
                logger.exception("[_start_game_services] failed registering critical service: {}".format(key))

        for key, service_tuple in service_manager.get_services_gen():
            try:
                service, early_load = service_tuple
                if early_load:
                    self.services.insert(0, service)
                else:
                    self.register_service(service, is_init_critical=False)
            except:
                logger.exception("[_start_game_services] failed registering service: {}".format(key))

        event_service.process_event(CoreEvent.GAME_SERVICES_STARTED)
    except:
        logger.exception("[_start_game_services] total failure")

    original(self, *args, **kwargs)
