import random
import alarms
import clock
import services
from date_and_time import create_time_span, DateAndTime, TimeSpan, create_date_and_time
from lot51_core import logger
from lot51_core.constants import DayOfWeek
from sims4.tuning.tunable import TunableVariant, TunableRange, HasTunableFactory, AutoFactoryInit, TunableTuple, \
    OptionalTunable, TunableEnumSet, Tunable, TunableInterval


class BaseTunableAlarm(HasTunableFactory, AutoFactoryInit):
    MINIMUM_INTERVAL = create_time_span(minutes=5)

    def __init__(self, owner, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.owner = owner
        self._callback = callback
        self._alarm_handle = None
        self._last_trigger = None
        self._last_span = None

    @property
    def scheduled(self):
        return self._alarm_handle is not None

    @property
    def last_trigger(self):
        return self._last_trigger

    @property
    def last_span(self):
        return self._last_span

    def get_finishing_time(self):
        if self._alarm_handle is not None:
            return self._alarm_handle.finishing_time

    def _alarm_callback(self, handle):
        if self._callback is not None:
            self._callback()

    def get_time_span(self, on_reschedule=False):
        raise NotImplementedError

    def start_internal(self, on_reschedule=False):
        sim_now = services.time_service().sim_now
        self._last_trigger = DateAndTime(sim_now.absolute_ticks())

        time_span = self.get_time_span(on_reschedule=on_reschedule)
        if time_span <= TimeSpan.ONE:
            logger.warn("[{}] Alarm is a performance risk. Preventing schedule from continuing.".format(self))
            return
        if time_span < self.MINIMUM_INTERVAL:
            time_span = self.MINIMUM_INTERVAL

        self._last_span = time_span
        self._alarm_handle = alarms.add_alarm(self, time_span, self._alarm_callback)
        return time_span

    def start(self):
        self.stop()
        return self.start_internal()

    def reschedule(self):
        self.stop()
        return self.start_internal(on_reschedule=True)

    def stop(self):
        if self._alarm_handle is not None:
            alarms.cancel_alarm(self._alarm_handle)
            self._alarm_handle = None


class TunableIntervalAlarm(BaseTunableAlarm):

    FACTORY_TUNABLES = {
        'days_available': TunableEnumSet(enum_type=DayOfWeek),
        'start_time': OptionalTunable(
            tunable=TunableTuple(
                hour=TunableRange(tunable_type=int, minimum=0, maximum=23, default=8),
                minutes=TunableRange(tunable_type=int, minimum=0, maximum=59, default=0),
            )
        ),
        'random_offset': OptionalTunable(
            tunable=TunableInterval(
                default_lower=0,
                default_upper=1440,
                tunable_type=int,
            ),
        ),
        'days': TunableRange(tunable_type=int, minimum=0, default=0),
        'hours': TunableRange(tunable_type=int, minimum=0, default=0),
        'minutes': TunableRange(tunable_type=int, minimum=0, default=0),
    }

    def is_day_available(self, now):
        if len(self.days_available) == 0:
            return True
        return DayOfWeek(now.day()) in self.days_available

    def get_time_span(self, on_reschedule=False):
        now = services.time_service().sim_now

        if self.random_offset is not None:
            random_offset = create_time_span(minutes=random.randint(self.random_offset.lower_bound, self.random_offset.upper_bound))
        else:
            random_offset = TimeSpan(0)

        if self.start_time is not None and not on_reschedule:
            time_span = clock.time_until_hour_of_day(now, self.start_time.hour) + create_time_span(minutes=self.start_time.minutes) + random_offset
        else:
            time_span = create_time_span(days=self.days, hours=self.hours, minutes=self.minutes) + random_offset

        schedule_time = now + time_span

        if not self.is_day_available(schedule_time):
            day = DayOfWeek(schedule_time.day())
            all_days = sorted({*self.days_available, day})
            day_ix = all_days.index(day)
            next_ix = 0 if day_ix == len(all_days) - 1 else day_ix + 1
            next_day = all_days[next_ix]
            offset_time = create_date_and_time(days=next_day)
            offset_span = schedule_time.time_to_week_time(offset_time)
        else:
            offset_span = TimeSpan.ZERO

        return offset_span + time_span


class TunableAlarmVariant(TunableVariant):
    VARIANT_TYPES = {
        'interval': TunableIntervalAlarm.TunableFactory(),
    }

    def __init__(self, *args, default=None, **kwargs):
        super().__init__(*args, **self.VARIANT_TYPES, default='interval', **kwargs)
