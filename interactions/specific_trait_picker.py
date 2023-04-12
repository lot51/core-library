"""
This file was written by Frankk (https://frankkmods.com).
Do not use or distribute this file without proper attribution.
"""
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet
from lot51_core import logger
from services import get_instance_manager
from sims4.resources import Types
from interactions import ParticipantTypeSim
from interactions.base.picker_interaction import PickerSuperInteraction
from sims4.tuning.tunable import Tunable, TunableEnumEntry, TunableList, TunableReference, TunableTuple
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from ui.ui_dialog_picker import ObjectPickerRow


class SpecificTraitPickerSuperInteraction(PickerSuperInteraction):
    """
    A picker that lets you choose specific traits rather than filtering by tag.
    """

    INSTANCE_TUNABLES = {
        'picker_target': TunableEnumEntry(
            tunable_type=ParticipantTypeSim,
            default=ParticipantTypeSim.TargetSim,
            tuning_group=GroupNames.PICKERTUNING
        ),
        'is_add': Tunable(
            description="If true, the trait will be added. If false, the trait will be removed.",
            tunable_type=bool,
            default=True
        ),
        'remove_others': Tunable(
            description="If true, all other traits will be removed upon picking this one.",
            tunable_type=bool,
            default=False
        ),
        'trait_choices': TunableList(
            description="A list of traits to pick from.",
            tunable=TunableTuple(
                traits=TunableList(
                    tunable=TunableReference(
                        manager=get_instance_manager(Types.TRAIT),
                        pack_safe=True
                    )
                ),
                tests=TunableTestSet(),
            )
        ),
        'show_description': Tunable(
            description="If true, the trait description will be displayed as the row description.",
            tunable_type=bool,
            default=False
        ),
    }

    def _run_interaction_gen(self, timeline):
        target_sim = self.get_participant(self.picker_target)
        self._show_picker_dialog(target_sim, target_sim=target_sim)
        return True

    @classmethod
    def _get_trait_choices(cls, target):
        resolver = SingleSimResolver(target)
        for item in cls.trait_choices:
            if item.tests.run_tests(resolver):
                for trait in item.traits:
                    if trait is not None:
                        yield trait

    @classmethod
    def _trait_selection_gen(cls, target):
        if cls.remove_others:
            yield from cls._get_trait_choices(target)
            return
        trait_tracker = target.sim_info.trait_tracker
        if cls.is_add:
            for trait in cls._get_trait_choices(target):
                if (not trait.sim_info_fixup_actions) and trait_tracker.can_add_trait(trait):
                    yield trait
        else:
            for trait in cls._get_trait_choices(target):
                if trait_tracker.has_trait(trait):
                    yield trait

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        target_sim = inst_or_cls.get_participant(inst_or_cls.picker_target, target=target, context=context, **kwargs)
        for trait in cls._trait_selection_gen(target_sim):
            row_description = trait.trait_description(target_sim) if inst_or_cls.show_description else None
            yield ObjectPickerRow(name=trait.display_name(target_sim), row_description=row_description, icon=trait.icon, tag=trait)

    def on_choice_selected(self, trait_to_change, **kwargs):
        try:
            if trait_to_change is not None:
                sim_info = self.get_participant(self.picker_target).sim_info
                if self.is_add:
                    if self.remove_others:
                        for trait_info in self.trait_choices:
                            for trait in trait_info.traits:
                                sim_info.remove_trait(trait)
                    sim_info.add_trait(trait_to_change)
                else:
                    sim_info.remove_trait(trait_to_change)
        except:
            logger.exception("[{}] Failed on picker response".format(self))
