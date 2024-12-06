# Learn how to create your own tests following Frankk's guide
# at https://frankkmods.medium.com/custom-tuning-tests-sims-4-script-modding-3837e214fb68
from lot51_core.tests.daytime import DaytimeTest
from lot51_core.tests.distance_2d import Distance2dTest
from lot51_core.tests.food_restriction import CustomFoodRestrictionTest
from lot51_core.tests.has_owned_zone import OwnedZoneThresholdTest
from lot51_core.tests.identity_comparison import IdentityComparisonTest
from lot51_core.tests.inventory_owner import InventoryOwnerTest
from lot51_core.tests.lock_out import AffordanceLockOutTest
from lot51_core.tests.lot import LotSizeTest
from lot51_core.tests.mood import MoodIntensityTest, MoodWeightTest
from lot51_core.tests.object_query import ObjectQueryTest
from lot51_core.tests.object_tuning import ObjectTuningTest
from lot51_core.tests.packs import PackTest
from lot51_core.tests.room import ObjectInRoomTest
from lot51_core.tests.situation_state import CustomStateSituationTest
from lot51_core.tests.situation_target_test import SituationTargetObjectTest
from lot51_core.tests.slots import ObjectSlotInUseTest
from lot51_core.tests.statistics import StatisticLockedTest
from lot51_core.tests.stolen import ObjectStolenTest
from lot51_core.tests.stored_sim_component import StoredSimComponentTest
from lot51_core.tests.terrain import TerrainTest
from lot51_core.tests.resource_test import ResourceExistenceTest
from lot51_core.tests.walkstyle import WalkstyleTest
from event_testing.tests import TestSetInstance, TunableTestVariant, _TunableTestSetBase


class LotFiftyOneCoreTestSet(_TunableTestSetBase, is_fragment=True):
    MY_TEST_VARIANTS = {
        'affordance_lock_out': AffordanceLockOutTest,
        'custom_food_restriction_test': CustomFoodRestrictionTest,
        'custom_state_situation_test': CustomStateSituationTest,
        'daytime': DaytimeTest,
        'distance_2d': Distance2dTest,
        'has_pack': PackTest,
        'identity_comparison': IdentityComparisonTest,
        'inventory_owner': InventoryOwnerTest,
        'lot_size': LotSizeTest,
        'mood_intensity': MoodIntensityTest,
        'mood_weight': MoodWeightTest,
        'object_in_room': ObjectInRoomTest,
        'object_query_test': ObjectQueryTest,
        'object_tuning_test': ObjectTuningTest,
        'object_slots_in_use': ObjectSlotInUseTest,
        'object_stolen': ObjectStolenTest,
        'owned_zone_threshold': OwnedZoneThresholdTest,
        'resource_existence': ResourceExistenceTest,
        'situation_target': SituationTargetObjectTest,
        'statistic_locked': StatisticLockedTest,
        'stored_sim_test': StoredSimComponentTest,
        'terrain_features': TerrainTest,
        'walkstyle': WalkstyleTest,
    }

    def __init__(self, **kwargs):
        for test_name, test in self.MY_TEST_VARIANTS.items():
            TunableTestVariant.TEST_VARIANTS[test_name] = test.TunableFactory
        super().__init__(test_locked_args={}, **kwargs)


class LotFiftyOneLibTestSetInstance(TestSetInstance):
    INSTANCE_TUNABLES = {'test': LotFiftyOneCoreTestSet()}
