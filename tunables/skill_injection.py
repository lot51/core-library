import services
from interactions import ParticipantType
from interactions.utils.tunable_provided_affordances import TunableProvidedAffordances
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.collections import AttributeDict
from lot51_core.utils.injection import merge_list, merge_mapping_lists, merge_dict, inject_dict
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableTuple, TunableMapping, TunableSet


class TunableSkillInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'skill': TunableReference(manager=services.get_instance_manager(Types.STATISTIC), pack_safe=True, class_restrictions=('Skill',)),
        'level_data': TunableMapping(
            key_type=int,
            value_type=TunableTuple(
                loot=TunableList(
                    tunable=TunableReference(
                        manager=services.get_instance_manager(Types.ACTION),
                        class_restrictions=('LootActions',),
                        pack_safe=True
                    )
                ),
                super_affordances=TunableSet(
                    tunable=TunableReference(
                        manager=services.get_instance_manager(Types.INTERACTION),
                        class_restrictions=('SuperInteraction',),
                        pack_safe=True
                    )
                ),
                target_super_affordances=TunableProvidedAffordances(
                    locked_args={
                        'target': ParticipantType.Object,
                        'carry_target': ParticipantType.Invalid,
                        'is_linked': False,
                        'unlink_if_running': False
                    }
                ),
                actor_mixers=TunableMapping(
                    key_type=TunableReference(
                        manager=services.get_instance_manager(Types.INTERACTION),
                        class_restrictions=('SuperInteraction',),
                        pack_safe=True
                    ),
                    value_type=TunableSet(
                        tunable=TunableReference(
                            manager=services.get_instance_manager(Types.INTERACTION),
                            category='asm',
                            class_restrictions=('MixerInteraction',),
                            pack_safe=True
                        )
                    )
                )
            )
        ),
    }

    __slots__ = ('skill', 'level_data')

    def inject(self):
        if self.skill is None:
            logger.warn("Skill not found to inject")
            return

        if len(self.level_data):
            new_level_data = dict()
            for skill_level_index, skill_level_data in tuple(self.skill.level_data.items()):
                user_level_data = self.level_data.get(skill_level_index, None)
                if user_level_data is None:
                    continue

                level_data_overrides = AttributeDict()

                if len(user_level_data.loot):
                    level_data_overrides.loot = merge_list(skill_level_data.loot, new_items=user_level_data.loot)

                if len(user_level_data.super_affordances):
                    level_data_overrides.super_affordances = merge_list(skill_level_data.super_affordances, new_items=user_level_data.super_affordances)

                if len(user_level_data.target_super_affordances):
                    level_data_overrides.target_super_affordances = merge_list(skill_level_data.target_super_affordances, new_items=user_level_data.super_affordances)

                if len(user_level_data.actor_mixers):
                    level_data_overrides.actor_mixers = merge_mapping_lists(skill_level_data.actor_mixers, user_level_data.actor_mixers)
                new_level_data[skill_level_index] = merge_dict(skill_level_data, new_items=level_data_overrides)
                # logger.debug("New Level Data: {} {}".format(skill_level_data, new_level_data[skill_level_index]))

            inject_dict(self.skill, 'level_data', new_items=new_level_data)