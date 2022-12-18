from interactions.utils.loot import LootActions, LootActionVariant, RandomWeightedLoot
from interactions.utils.success_chance import SuccessChance
from lot51_core import logger
from lot51_core.loot.actions_by_object_source import DoActionsByObjectSource
from lot51_core.loot.balloons import BalloonLoot
from lot51_core.loot.camera import CameraFocusLoot
from lot51_core.loot.game_clock import GameClockSpeedLoot
from lot51_core.loot.notification import SingleNotification
from lot51_core.loot.purchase_picker import OpenPurchasePickerLoot
from lot51_core.loot.spawn_object import CreateObjectRingLoot, SpawnObjectLoot
from lot51_core.loot.transform_object import TransformObjectLoot
from lot51_core.utils.math import chance_succeeded
from interactions.utils.loot_ops import DoNothingLootOp
from sims4.tuning.tunable import TunableList, OptionalTunable, TunableTuple
from sims4.utils import flexmethod
from tunable_multiplier import TunableMultiplier


class LotFiftyOneCoreLootActionVariant(LootActionVariant):

    LOOT_VARIANTS = {
        'actions_by_object_source': DoActionsByObjectSource.TunableFactory(),
        'balloon': BalloonLoot.TunableFactory(),
        'camera_focus': CameraFocusLoot.TunableFactory(),
        'clock_speed': GameClockSpeedLoot.TunableFactory(),
        'create_object_ring': CreateObjectRingLoot.TunableFactory(),
        'open_purchase_picker': OpenPurchasePickerLoot.TunableFactory(),
        'single_notification': SingleNotification.TunableFactory(),
        'spawn_object': SpawnObjectLoot.TunableFactory(),
        'transform_object': TransformObjectLoot.TunableFactory(),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, statistic_pack_safe=True, **kwargs, **self.LOOT_VARIANTS)


class LotFiftyOneCoreRandomWeightedLoot(RandomWeightedLoot):
    INSTANCE_TUNABLES = {
        'random_loot_actions': TunableList(
            tunable=TunableTuple(
                action=LotFiftyOneCoreLootActionVariant(do_nothing=DoNothingLootOp.TunableFactory()),
                weight=TunableMultiplier.TunableFactory(),
            )
        )
    }


class LotFiftyOneCoreLootActions(LootActions):

    INSTANCE_TUNABLES = {
        'loot_actions': TunableList(
            description='List of loot operations that will be awarded.',
            tunable=LotFiftyOneCoreLootActionVariant()
        ),
        'chance': OptionalTunable(
            tunable=SuccessChance.TunableFactory(),
        ),
    }

    FACTORY_TUNABLES = INSTANCE_TUNABLES

    def __repr__(self):
        return f"<LotFiftyOneCoreLootActions:({self.__name__})>"

    def __str__(self):
        return f"{self.__name__}"

    @flexmethod
    def get_loot_ops_gen(cls, inst, resolver=None, **kwargs):
        try:
            inst_or_cls = inst if inst is not None else cls
            if inst_or_cls.chance is not None:
                chance = inst_or_cls.chance.get_chance(resolver)
                if not chance_succeeded(chance):
                    return
        except Exception as e:
            logger.error(f"Error while running loot: {cls}\n{str(e)}")
        yield from super().get_loot_ops_gen(resolver=resolver, **kwargs)
