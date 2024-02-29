from collections import defaultdict
from lot51_core import logger


class InjectionTracker:

    def __init__(self):
        self._cache = defaultdict(set)

    def can_inject(self, owner_tuning, tunable_key):
        if owner_tuning is not None and tunable_key is not None:
            if owner_tuning not in self._cache or tunable_key not in self._cache[owner_tuning]:
                return True
        return False

    def inject(self, owner_tuning, tunable_key, safe=True):
        """
        Check if a tunable has been injected to previously. This function assumes an injection will perform if
        it returns True and will track the change preventing future injections. A warning will be logged if a previous
        injection was detected. Use `can_inject` if you want to perform a simple test.

        :param owner_tuning: The tuning to check against.
        :param tunable_key: The key of the owner_tuning to track changes.
        :param safe: When safe, this function will return False if previously injected.
        :return: Returns True if the injection was performed.
        """
        if owner_tuning is not None and tunable_key is not None:
            if self.can_inject(owner_tuning, tunable_key):
                self._cache[owner_tuning].add(tunable_key)
                return True
            else:
                logger.warn("Key {} on Tuning {} has already been previously overwritten. Skipping injection: {}".format(tunable_key, owner_tuning, safe))
                if not safe:
                    return True
        return False

    def cleanup(self):
        self._cache.clear()


injection_tracker = InjectionTracker()