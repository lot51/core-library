import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableSet, TunableTuple, Tunable


class TunableDynastyValueInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'dynasty_values': TunableList(
            description="The DynastyValues to inject to",
            tunable=TunableReference(manager=services.get_instance_manager(Types.SNIPPET), pack_safe=True, class_restrictions=('DynastyValue',))
        ),
        'trait_modifiers': TunableList(
            tunable=TunableTuple(
                trait=TunableReference(manager=(services.get_instance_manager(Types.TRAIT)), pack_safe=True),
                value=Tunable(tunable_type=float, default=0)
            )
        ),
        'aligned_activities':TunableList(
           tunable=TunableReference(manager=services.get_instance_manager(Types.CLUB_INTERACTION_GROUP), pack_safe=True)
        ),
        'misaligned_activities':TunableList(
           tunable=TunableReference(manager=services.get_instance_manager(Types.CLUB_INTERACTION_GROUP), pack_safe=True)
        ),
        'values_matching':TunableSet(
           tunable=TunableReference(
           manager=services.get_instance_manager(Types.SNIPPET), class_restrictions=('DynastyValue', ), pack_safe=True)
        ),
        'values_conflicting': TunableSet(
           tunable=TunableReference(
           manager=services.get_instance_manager(Types.SNIPPET), class_restrictions=('DynastyValue', ), pack_safe=True)
        ),
        'career_tracks_aligned_visible': TunableSet(
           tunable=TunableReference(manager=services.get_instance_manager(Types.CAREER_TRACK), pack_safe=True)
        ),
        'career_tracks_aligned_hidden': TunableSet(
           tunable=TunableReference(manager=services.get_instance_manager(Types.CAREER_TRACK), pack_safe=True)
        ),
        'career_tracks_misaligned_visible': TunableSet(
           tunable=TunableReference(manager=services.get_instance_manager(Types.CAREER_TRACK), pack_safe=True)
        ),
        'career_tracks_misaligned_hidden': TunableSet(
           tunable=TunableReference(manager=services.get_instance_manager(Types.CAREER_TRACK), pack_safe=True)
        ),
        'loot_on_dynasty_value_removed': TunableList(
           tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True)
        ),
        'loot_on_dynasty_value_added': TunableList(
           tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True)
        ),
    }

    __slots__ = ('dynasty_values', 'trait_modifiers', 'aligned_activities', 'misaligned_activities', 'values_matching', 'values_conflicting', 'career_tracks_aligned_visible', 'career_tracks_aligned_hidden', 'career_tracks_misaligned_visible', 'career_tracks_misaligned_hidden', 'loot_on_dynasty_value_removed', 'loot_on_dynasty_value_added',)

    def inject(self):
        for snippet in self.dynasty_values:
            inject_list(snippet, 'trait_modifiers', self.trait_modifiers)
            inject_list(snippet, 'aligned_activities', self.aligned_activities)
            inject_list(snippet, 'misaligned_activities', self.misaligned_activities)
            inject_list(snippet, 'values_matching', self.values_matching)
            inject_list(snippet, 'values_conflicting', self.values_conflicting)
            inject_list(snippet, 'career_tracks_aligned_visible', self.career_tracks_aligned_visible)
            inject_list(snippet, 'career_tracks_aligned_hidden', self.career_tracks_aligned_hidden)
            inject_list(snippet, 'career_tracks_misaligned_visible', self.career_tracks_misaligned_visible)
            inject_list(snippet, 'career_tracks_misaligned_hidden', self.career_tracks_misaligned_hidden)
            inject_list(snippet, 'loot_on_dynasty_value_removed', self.loot_on_dynasty_value_removed)
            inject_list(snippet, 'loot_on_dynasty_value_added', self.loot_on_dynasty_value_added)