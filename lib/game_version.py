import os
import re
import enum
import sims4.reload
from lot51_core.utils.paths import get_game_dir
from lot51_core.utils.semver import Version, _cmp

with sims4.reload.protected(globals()):
    cached_version = None


class Platform(enum.Int):
    WINDOWS = 10
    MAC = 12
    WINDOWS_LEGACY = 15
    MAC_LEGACY = 16


class GameVersion:
    """
    A class to parse and test a game version. Supports
    semver style match, with helper methods to convert
    to SemVer object, or tuple.
    """
    GAME_VERSION_REGEX = re.compile(r"^(?P<major>\d{1})\.(?P<minor>\d{1,3})\.(?P<patch>\d{1,3})(?:\.(?P<platform>(?P<os>10|12|15|16)(?P<unused>10|20|30)))?$")
    # GAME_VERSION_REGEX = re.compile(r"^(?P<major>\d{1})\.(?P<minor>\d{1,3})\.(?P<patch>\d{1,3})\.(?P<platform>(?P<os>10|12|15|16)(?P<unused>10|20|30))$")

    def __init__(self, major=None, minor=None, patch=None, platform=None, os=None, unused=None):
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)
        self.platform = int(platform) if platform is not None else None
        self.os = int(os) if os is not None else None
        self.unused = int(unused) if unused is not None else None

    def __str__(self):
        return self.to_str()

    def compare(self, other):
        cls = type(self)
        if isinstance(other, str):
            other = cls.parse(other)
        elif isinstance(other, dict):
            other = cls(**other)
        elif isinstance(other, (tuple, list,)):
            other = cls(*other)
        elif not isinstance(other, (cls, Version,)):
            raise TypeError(
                f"Expected str, dict, tuple, list, Version, or {cls.__name__} instance, "
                f"but got {type(other)}"
            )

        v1 = self.to_tuple()[:3]
        v2 = other.to_tuple()[:3]
        return _cmp(v1, v2)

    def __eq__(self, other):
        return self.compare(other) == 0

    def __ne__(self, other):
        return self.compare(other) != 0

    def __lt__(self, other):
        return self.compare(other) < 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __ge__(self, other):
        return self.compare(other) >= 0

    @classmethod
    def parse(cls, version):
        match = cls.GAME_VERSION_REGEX.match(version)
        if match is not None:
            match_opts = match.groupdict()
            return cls(**match_opts)
        else:
            raise ValueError("Invalid version")

    @classmethod
    def test(cls, version: str):
        return bool(cls.GAME_VERSION_REGEX.match(version))

    def is_valid(self):
        return self.test(str(self))

    def is_windows(self):
        return self.os in (Platform.WINDOWS, Platform.WINDOWS_LEGACY,)

    def is_mac(self):
        return self.os in (Platform.MAC, Platform.MAC_LEGACY,)

    def is_legacy(self):
        return self.os in (Platform.WINDOWS_LEGACY, Platform.MAC_LEGACY,)

    def match(self, match_expr: str):
        return self.to_semver().match(match_expr)

    def clone(self):
        return GameVersion(**self.to_dict())

    def to_semver(self):
        return Version(major=self.major, minor=self.minor, patch=self.patch)

    def to_str(self, include_platform=True):
        version = '%d.%d.%d' % (self.major, self.minor, self.patch)
        if include_platform:
            version += '.%d' % self.platform
        return version

    def to_tuple(self):
        return self.major, self.minor, self.patch, self.platform

    def to_dict(self):
        return dict(
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            platform=self.platform,
            os=self.os,
            unused=self.unused,
        )


def fetch_game_version(root=None):
    """
    Attempts to read the GameVersion.txt file
    from the Game document directory.

    :return: string
    """
    if root is None:
        root = get_game_dir()
    path = os.path.join(root, 'GameVersion.txt')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        # Remove special characters
        text = re.sub('[^0-9.]+', '', text)
        return text
    except:
        pass


def get_game_version():
    """
    Get the current version of The Sims 4 installation.

    :return: GameVersion
    """
    global cached_version
    # Prevent unnecessary file load if
    # version previously failed to fetch
    if cached_version == -1:
        return None
    # Fetch cached raw version
    if cached_version is not None:
        return GameVersion.parse(cached_version)
    # Get raw game version and parse
    raw_version = fetch_game_version()
    if raw_version is not None:
        cached_version = raw_version
        return GameVersion.parse(raw_version)
    # Failed to load raw version
    cached_version = -1
    return None


def is_game_version(match_expr: str):
    """
    Test the current game version against a version match expression.
    Example: test_game_version(">=1.105.0")

     :param match_expr: optional operator and version; valid operators are
          ``<```   smaller than
          ``>``   greater than
          ``>=``  greator or equal than
          ``<=``  smaller or equal than
          ``==``  equal
          ``!=``  not equal
    :return: True if the expression matches the current game version, otherwise False
    """
    game_version = get_game_version()
    return game_version.match(match_expr)
