import logging
import os
import lot51_core
from lot51_core.lib.game_version import get_game_version


def Logger(name, root, filename, version='N/A', mode='development'):
    path = os.path.join(root, filename)
    handler = logging.FileHandler(path, mode='w')
    log_mode = logging.DEBUG if mode == 'development' else logging.INFO

    formatter = logging.Formatter('[%(levelname)s] %(message)s')

    logger = logging.getLogger(name)
    logger.setLevel(log_mode)
    logger.addHandler(handler)
    handler.setFormatter(formatter)

    logger.info('[Lot 51] {name}; version: {version}; mode: {mode}; library: {lib}; game version: {game_version}'.format(
        name=name, version=version, mode=mode, lib=lot51_core.__version__, game_version=get_game_version()))
    logger.info('If you are experiencing any issues with this mod, please join my Discord at https://lot51.cc/discord and report your error in #mod-support with this log.')
    return logger


def stringify_sim_info(sim_info):
    """
    DEPRECATED. Use lot51_core.lib.sim.get_sim_name instead.
    """
    from lot51_core.lib.sims import get_sim_name
    return get_sim_name(sim_info)


def stringify_sim(sim):
    """
    DEPRECATED. Use lot51_core.lib.sim.get_sim_name instead.
    """
    from lot51_core.lib.sims import get_sim_name
    return get_sim_name(sim)
