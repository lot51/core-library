from event_testing.resolver import SingleObjectResolver
from interactions.choices import ChoiceMenu
from lot51_core import logger
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from lot51_core.utils.injection import inject_to, obj_has_affordance
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableReference, TunableList, TunableTuple, HasTunableReference, OptionalTunable


class TestedPieMenuForwarding(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=get_instance_manager(Types.SNIPPET)):
    INSTANCE_TUNABLES = {
        'forward_data': TunableList(
            tunable=TunableTuple(
                affordances=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.INTERACTION), pack_safe=True)
                ),
                pie_menu_category=OptionalTunable(
                    tunable=TunableReference(manager=get_instance_manager(Types.PIE_MENU_CATEGORY))
                ),
                object_query=ObjectSearchMethodVariant(),
            )
        )
    }

    __slots__ = ('forward_data',)

    @classmethod
    def all_snippets_gen(cls):
        yield from get_instance_manager(Types.SNIPPET).get_ordered_types(only_subclasses_of=TestedPieMenuForwarding)

    @classmethod
    def add_additional_aops(cls, add_potential_aops, target, context):
        resolver = SingleObjectResolver(target)
        shift_held = context.shift_held if context is not None else False
        for row in cls.forward_data:
            for obj in row.object_query.get_objects_gen(resolver=resolver):
                for affordance in row.affordances:
                    if obj._can_show_affordance(shift_held, affordance):
                        potential_aops = affordance.potential_interactions(obj, context)
                        add_potential_aops(potential_aops, obj)


@inject_to(ChoiceMenu, 'add_potential_aops')
def _add_potential_aops(original, self, target, context, potential_aops, *args, **kwargs):
    original(self, target, context, potential_aops, *args, **kwargs)
    try:
        def add_aops(aops, trgt):
            original(self, trgt, context, aops, *args, **kwargs)

        for snippet in TestedPieMenuForwarding.all_snippets_gen():
            snippet.add_additional_aops(add_aops, target, context)
    except:
        logger.exception("Failed adding potential aops")
