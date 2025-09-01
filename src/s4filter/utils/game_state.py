import paths
from lot51_core.utils.flags import Flag
import os
import base64
import enum


class GameStateFlag(enum.Int):
    FLAG1 = 1 # Game Offline
    FLAG2 = 1 << 2 # Steam
    FLAG3 = 1 << 3
    FLAG4 = 1 << 4
    FLAG5 = 1 << 5
    FLAG6 = 1 << 6


def thwbbvv5d():
    data_path = paths.APP_ROOT.lower() + ':' + paths.DATA_ROOT.lower()
    possible_strings = {
        b'Y3JhY2tlZA==',
        b'YW5hZGl1cw==',
    }
    for i, p in enumerate(possible_strings):
        decoded = base64.b64decode(p).decode('utf-8').lower()
        if decoded in data_path:
            return True
        if i == 0 and decoded in os.environ.get('EALaunchEAID', ''):
            return True

    if os.name == 'nt':
        path_list = {
            b'L0FwcGxpY2F0aW9ucy9hbmFkaXVzIHRvb2xz',
            b'fi9EZXNrdG9wL2FuYWRpdXMgdG9vbHM=',
        }
    else:
        path_list = {
            b'fi9EZXNrdG9wL2FuYWRpdXMgdG9vbHM=',
            b'fi9Eb3dubG9hZHMvYW5hZGl1cyB0b29scw==',
            b'L0FwcGxpY2F0aW9ucy9hbmFkaXVzIHRvb2xz',
            b'L0FwcGxpY2F0aW9ucy9hbmFkaXVzIHRvb2xzLmFwcA==',
            b'flxBcHBEYXRhXExvY2FsXGFuYWRpdXM=',
            b'fi9EZXNrdG9wL2FuYWRpdXMgdG9vbHMuYXBw',
            b'fi9hbmFkaXVzIHRvb2xz',
            b'flxBcHBEYXRhXFJvYW1pbmdcYW5hZGl1cw==',
            b'fi9Eb3dubG9hZHMvYW5hZGl1cyB0b29scy5hcHA=',
            b'fi9hbmFkaXVzIHRvb2xzLmFwcA==',
        }
    for p in path_list:
        e = os.path.expanduser(base64.b64decode(p))
        try:
            if os.path.exists(e):
                return True
        except:
            pass
    return False


def get_game_state_flag():
    flag = Flag()
    try:
        if os.environ.get('EALaunchOfflineMode', 'false') == 'true':
            flag.add(GameStateFlag.FLAG1)
        if os.environ.get('SteamAppId', None):
            flag.add(GameStateFlag.FLAG2)
        if thwbbvv5d():
            flag.add(GameStateFlag.FLAG3)
    except:
        pass
    return flag
