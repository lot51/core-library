import os
import json
from lot51_core.utils.collections import AttributeDict


class Config:
    def __init__(self, root_path, config_filename, logger, default_data: dict = dict()):
        self._config = dict()
        self._default_data = dict(default_data)
        self._root_path = root_path
        self.logger = logger
        self._config_filename = config_filename
        self.load()

    @property
    def config_filename(self):
        return self._config_filename

    def load(self):
        self._root_path = self.get_root_path()
        self._config = self._load_config_file()
        # self.logger.debug('[Config] init')

    def save(self):
        if not self._config or not self._root_path:
            return False
        try:
            self._save_config_file(self._config)
            return True
        except:
            self.logger.exception('[Config] failed to save')
        return False

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

    def get_root_path(self):
        if not os.path.exists(self._root_path):
            os.makedirs(self._root_path)
        return self._root_path

    def _save_config_file(self, data):
        with open(os.path.join(self.get_root_path(), self.config_filename), 'w', encoding='utf-8') as f:
            json.dump(data, f)
            return True

    def _parse_value(self, value):
        if type(value) is dict:
            value = AttributeDict(value)
            for key, nested_value in value.items():
                value[key] = self._parse_value(nested_value)
            return value
        return value

    def _load_config_file(self):
        try:
            full_path = os.path.join(self.get_root_path(), self.config_filename)
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
                if data:
                    return self._parse_value(data)
        except:
            self.logger.warn('[Config] using default data')
        return dict(self._default_data)
