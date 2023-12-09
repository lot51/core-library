from sims4.tuning.tunable_perf import TuningAttrCleanupHelper


"""
Issue introduced in 1.103.250

Fix created by Frankk & TURBODRIVER
to prevent errors when manually initializing Dialogs
(i.e. the DialogHelper class in this library)
"""
if not hasattr(TuningAttrCleanupHelper, "_original_register_for_cleanup"):
    TuningAttrCleanupHelper._original_register_for_cleanup = TuningAttrCleanupHelper.register_for_cleanup

    def new_register_for_cleanup(self, *args, **kwargs):
        if self._tracked_objects is None:
            return
        return self._original_register_for_cleanup(*args, **kwargs)

    TuningAttrCleanupHelper.register_for_cleanup = new_register_for_cleanup