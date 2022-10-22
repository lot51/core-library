from interactions.utils.loot import LootActions, LootActionVariant
from interactions.utils.success_chance import SuccessChance
from lot51_core import logger
from lot51_core.loot.actions_by_object_source import DoActionsByObjectSource
from lot51_core.loot.notification import SingleNotification
from lot51_core.utils.math import chance_succeeded
from sims4.tuning.tunable import TunableList, OptionalTunable
from sims4.utils import flexmethod


class LotFiftyOneCoreLootActionVariant(LootActionVariant):

    LOOT_VARIANTS = {
        'actions_by_object_source': DoActionsByObjectSource.TunableFactory(),
        'single_notification': SingleNotification.TunableFactory()
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, statistic_pack_safe=True, **kwargs, **self.LOOT_VARIANTS)


class LotFiftyOneCoreLootActions(LootActions):

    INSTANCE_TUNABLES = {
        'loot_actions': TunableList(
            description='List of loot operations that will be awarded.',
            tunable=LotFiftyOneCoreLootActionVariant()
        ),
        'chance': OptionalTunable(
            tunable=SuccessChance.TunableFactory(),
        )
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
        yield from super().get_loot_ops_gen(**kwargs)