import services
from _sims4_collections import frozendict
from lot51_core.tunables.base_injection import BaseTunableInjection
from seasons.season import DayOfSeason
from seasons.seasons_enums import SeasonLength
from sims4.common import Pack
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableTuple, TunableList, TunableEnumEntry


class TunableSeasonInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'season':TunableReference(manager=services.get_instance_manager(Types.SEASON)),
        'holidays': TunableList(
            tunable=TunableTuple(
                holiday=TunableReference(manager=services.get_instance_manager(Types.HOLIDAY_DEFINITION)),
                length_content=TunableList(
                    tunable=TunableTuple(
                        length=TunableEnumEntry(tunable_type=SeasonLength, default=SeasonLength.NORMAL),
                        day_of_season=DayOfSeason.TunableFactory(),
                    )
                ),
            )
        )
    }

    __slots__ = ('season', 'holidays',)

    @property
    def required_packs(self):
        return (Pack.EP05,)

    def inject(self):
        if self.season is not None:
            seasonal_content = self.season.season_length_content
            for holiday_data in self.holidays:
                if holiday_data.holiday is None:
                    continue
                for content in holiday_data.length_content:
                    length_content = seasonal_content.length_content[content.length]
                    holiday_dict = dict(length_content.holidays) if length_content.holidays is not None else dict()
                    holiday_dict[holiday_data.holiday] = (content.day_of_season,)
                    length_content.holidays = frozendict(holiday_dict)
