import pickle
import services
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_spawner import SimSpawner, SimCreator
from sims4 import hash_util
from sims4.callback_utils import CallableList


class SaveBasedConfig:

    def __init__(self, config_name, logger, default_data: dict = dict()):
        self._config = dict()
        self._config_name = config_name
        self._default_data = dict(default_data)
        self._config_load_callbacks = CallableList()
        self.logger = logger

    @property
    def household_name(self):
        return str(hash_util.hash32(self._config_name))

    def load(self):
        data = self._load()
        if data is not None:
            self._config = data
        else:
            self._config = dict(self._default_data)
        self._config_load_callbacks()

    def add_listener(self, listener):
        self._config_load_callbacks.register(listener)

    def remove_listener(self, listener):
        self._config_load_callbacks.unregister(listener)

    def save(self):
        self._save(self._config)

    def get(self, key, default=None):
        if key in self._config:
            val = self._config.get(key)
            if val is None:
                return default
            return val
        return default

    def set(self, key, value):
        self._config[key] = value
        return True

    def set_hard(self, key, value):
        self._config[key] = value
        return self.save()

    def _find_household(self):
        for household in services.household_manager().values():
            if household.name == self.household_name:
                return household

    def _create_household(self):
        (sim_info_list, new_household) = SimSpawner.create_sim_infos((SimCreator(),), zone_id=0)
        sim_info_list[0].request_lod(SimInfoLODLevel.MINIMUM)
        new_household.set_to_hidden()
        new_household.name = self.household_name
        new_household.description = ''
        return new_household

    def find_or_create_household(self):
        household = self._find_household()
        if household:
            self.logger.debug("found save based config household: {}".format(household))
            return household
        household = self._create_household()
        if household:
            self.logger.debug("created save based config household: {}".format(household))
            return household
        raise Exception("Failed to create household")

    def _load(self):
        household = self.find_or_create_household()
        # self.logger.debug("household description is: {}".format(household.description))
        serialized = bytes(household.description, encoding='latin1')
        # self.logger.debug("loaded save based config data: {}".format(serialized))
        try:
            return pickle.loads(serialized)
        except EOFError:
            return None

    def _save(self, data):
        household = self.find_or_create_household()
        serialized = str(pickle.dumps(data), encoding='latin1')
        household.description = serialized
        # self.logger.debug("set save based config data: {} -> {}".format(data, serialized))
