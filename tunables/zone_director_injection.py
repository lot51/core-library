import services
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list, merge_list, merge_dict
from lot51_core.utils.tunables import clone_factory_with_overrides
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableSet, TunableMapping, TunableTuple, Tunable, \
    OptionalTunable, TunableRange
from situations.situation_shifts import SituationShifts
from tag import TunableTag
from zone_modifier.zone_modifier_actions import ZoneModifierUpdateAction


class TunableZoneDirectorInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'zone_director': TunableReference(manager=services.get_instance_manager(Types.ZONE_DIRECTOR)),
        'additional_object_shift_data': TunableMapping(
            description="New shift data for object tags that DO NOT exist in the Zone Director's object_situation_shifts map.",
            key_name='object_tag',
            key_type=TunableTag(),
            value_name='shift_data',
            value_type=TunableTuple(
                schedule_immediate=Tunable(
                    tunable_type=bool,
                    default=True
                ),
                consider_off_lot_objects=Tunable(
                    tunable_type=bool,
                    default=True
                ),
                affected_object_cap=TunableRange(
                    tunable_type=int,
                    minimum=1,
                    default=1
                ),
                include_objects_within_object_inventories=OptionalTunable(
                    tunable=TunableList(
                        tunable=TunableTag(filter_prefixes=('func',))
                    )
                ),
                **SituationShifts.FACTORY_TUNABLES
            )
        ),
        'additional_object_situation_shifts': TunableMapping(
            description="Additional situation shifts for object tags that already exist in the Zone Director's object_situation_shifts map. Only situation_shifts are merged in to prevent conflicts.",
            key_name='object_tag',
            key_type=TunableTag(),
            value_name='shift_data',
            value_type=TunableTuple(
                **SituationShifts.FACTORY_TUNABLES
            )
        )
    }

    __slots__ = ('zone_director', 'additional_object_shift_data', 'additional_object_situation_shifts')

    def inject(self):
        if self.zone_director is None:
            logger.warn("[TunableZoneDirectorInjection] Zone director not found")
            return

        object_situation_shifts = getattr(self.zone_director, 'object_situation_shifts', None)
        if object_situation_shifts is not None:
            object_situations = dict(object_situation_shifts.object_situations)
            logger.info("Original Situations: {}".format(object_situations))

            for object_tag, shift_data in self.additional_object_shift_data.items():
                if object_tag not in object_situations:
                    object_situations[object_tag] = shift_data
                else:
                    logger.warn("[TunableZoneDirectorInjection] Object tag ({}) in `additional_object_shift_data` is already in zone director ({}) object situation shift data. Use `additional_object_situation_shifts` to modify existing tags".format(object_tag, self.zone_director))

            for object_tag, shift_data in self.additional_object_situation_shifts.items():
                if object_tag in object_situations:
                    zd_shift_data = object_situations[object_tag]
                    merged_situation_shifts = merge_list(zd_shift_data.situation_shifts, new_items=shift_data.situation_shifts)
                    cloned_shift_data = merge_dict(zd_shift_data, situation_shifts=merged_situation_shifts)
                    object_situations[object_tag] = cloned_shift_data
                    # logger.info("Merged Shifts: {} {}".format(object_tag, merged_situation_shifts))
                else:
                    logger.warn("[TunableZoneDirectorInjection] Object tag ({}) in `additional_object_situation_shifts` is not in zone director ({}) object situation shift data. Use `additional_object_shift_data` if you are adding a new object tag.".format(object_tag, self.zone_director))

            new_object_situation_shifts = merge_dict(self.zone_director.object_situation_shifts, object_situations=merge_dict(object_situation_shifts.object_situations, new_items=object_situations))
            setattr(self.zone_director, 'object_situation_shifts', new_object_situation_shifts)