import services
from date_and_time import DateAndTime
from datetime import datetime, timezone


def get_sunrise_time() -> DateAndTime:
    region = services.current_region()
    return region.get_sunrise_time()


def get_sunset_time() -> DateAndTime:
    region = services.current_region()
    return region.get_sunset_time()


def get_start_of_day(sim_now: DateAndTime):
    return DateAndTime(sim_now.absolute_ticks() - sim_now._ticks_in_day())


def get_absolute_sunrise_time(sim_now: DateAndTime) -> DateAndTime:
    sunrise_time = get_sunrise_time()
    return DateAndTime(get_start_of_day(sim_now).absolute_ticks() + sunrise_time._ticks_in_day())


def get_absolute_sunset_time(sim_now: DateAndTime) -> DateAndTime:
    sunset_time = get_sunset_time()
    return DateAndTime(get_start_of_day(sim_now).absolute_ticks() + sunset_time._ticks_in_day())


def get_wallclock_now(use_local_time=False, **kwargs):
    if use_local_time:
        return datetime.now()
    now = datetime.now(timezone.utc)
    utc_time = now.replace(tzinfo=timezone.utc)
    return utc_time