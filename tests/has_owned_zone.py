import build_buy
from caches import cached_test
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from event_testing.test_events import TestEvent
from interactions import ParticipantTypeSingle
from lot51_core import logger
from lot51_core.lib.sims import get_sim_info
from lot51_core.lib.zone import get_zone_data_gen, get_lot_owner_household_account_pair_from_zone_data
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableThreshold, TunableList, TunableReference, TunableEnumEntry


class OwnedZoneThresholdTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (TestEvent.SimTravel,)

    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Actor),
        'required_venues': TunableList(
            tunable=TunableReference(manager=get_instance_manager(Types.VENUE)),
        ),
        'threshold': TunableThreshold(description="The threshold that must be met")
    }

    __slots__ = ('subject', 'required_venues', 'threshold',)

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects=(), resolver=None, **kwargs):
        subject = next(iter(subjects))
        sim_info = get_sim_info(subject)
        venue_manager = get_instance_manager(Types.VENUE)
        total_owned = 0

        for zone_data in get_zone_data_gen():
            venue = venue_manager.get(build_buy.get_current_venue(zone_data.zone_id))
            if self.required_venues and venue not in self.required_venues:
                continue
            lot_owner_info = get_lot_owner_household_account_pair_from_zone_data(zone_data)
            household_id = lot_owner_info.household_id if lot_owner_info is not None else None
            if household_id == sim_info.household_id:
                total_owned += 1

        threshold_met = self.threshold.compare(total_owned)
        if not threshold_met:
            return TestResult(False, "Owned zone count does not meet threshold", tooltip=self.tooltip)
        return TestResult.TRUE