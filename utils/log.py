import logging
import os
import lot51_core


def Logger(name, root, filename, version='N/A', mode='development'):
    path = os.path.join(root, filename)
    handler = logging.FileHandler(path, mode='w')
    log_mode = logging.DEBUG if mode == 'development' else logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(log_mode)
    logger.addHandler(handler)

    logger.info('[Lot 51] {name}; version: {version}; mode: {mode}; library: {lib}'.format(name=name, version=version, mode=mode, lib=lot51_core.__version__))
    logger.info('If you are experiencing any issues with this mod, please go to https://lot51.cc and report your error with this log. Feel free to upload through the website, or join the Discord help channel.')
    return logger
