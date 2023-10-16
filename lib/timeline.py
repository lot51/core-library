import clock
import services
from element_utils import CleanupType, build_element
from elements import SoftSleepElement


def fade_and_destroy_object(target, duration=1, delay=0, timeline=None):
    sequence = []
    if delay > 0:
        sequence.append(SoftSleepElement(clock.interval_in_sim_minutes(delay)))

    def _handle_fade_out(h, dur=duration, trgt=target):
        if trgt is not None:
            trgt.fade_out(fade_duration=dur)

    def _handle_destroy(h, trgt=target):
        if trgt is not None:
            trgt.schedule_destroy_asap()

    sequence.append(_handle_fade_out)
    sequence.append(SoftSleepElement(clock.interval_in_sim_minutes(duration)))
    sequence.append(_handle_destroy)
    element = build_element(sequence, critical=CleanupType.RunAll)
    if timeline is None:
        timeline = services.time_service().sim_timeline
    timeline.schedule(element)
