from lot51_core.utils.log import Logger
from lot51_core.utils.paths import get_mod_root

__copyright__ = 'Copyright 2022, Lot 51'
__version__ = '1.34.1'
__author__ = 'Lot 51'
__email__ = 'hello@lot51.cc'
__status__ = 'production'
__minimum_game_version__ = '1.105.332'

ROOT_PATH = get_mod_root(__file__)
DEFAULT_CONFIG_FILENAME = 'lot51_core.dat'
DEFAULT_LOGS_FILENAME = 'lot51_core.log'

logger = Logger('Core Library', ROOT_PATH, DEFAULT_LOGS_FILENAME, mode=__status__, version=__version__, is_first_party=True)
