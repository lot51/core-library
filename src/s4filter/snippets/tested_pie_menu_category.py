import enum
from event_testing.resolver import SingleActorAndObjectResolver
from event_testing.tests import TunableTestSet
from interactions.choices import ChoiceMenu
from lot51_core import logger
from lot51_core.utils.injection import inject_to
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableReference, TunableList, TunableTuple, TunableEnumEntry


class PieMenuCategoryCompatibility(enum.Int):
    ANY = 0
    TARGET_ONLY = 1
    FORWARDED_ONLY = 2


class TestedPieMenuCategories(metaclass=HashedTunedInstanceMetaclass, manager=get_instance_manager(Types.SNIPPET)):
    INSTANCE_TUNABLES = {
        'categories': TunableList(
            tunable=TunableTuple(
                new_pie_menu_category=TunableReference(manager=get_instance_manager(Types.PIE_MENU_CATEGORY)),
                affordance_compatibility=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.INTERACTION))
                ),
                basic_compatibility=TunableEnumEntry(tunable_type=PieMenuCategoryCompatibility, default=PieMenuCategoryCompatibility.ANY),
                tests=TunableTestSet(),
            )
        )
    }

    __slots__ = ('categories',)

    @classmethod
    def all_snippets_gen(cls):
        yield from get_instance_manager(Types.SNIPPET).get_ordered_types(only_subclasses_of=TestedPieMenuCategories)

    @classmethod
    def get_category(cls, affordance, resolver, from_inventory_to_owner=False):
        for snippet in cls.all_snippets_gen():
            for row in snippet.categories:
                # check if affordance is in the compatibility list
                if affordance not in row.affordance_compatibility:
                    continue
                # check if compatible with forwarded setting
                if (row.basic_compatibility == PieMenuCategoryCompatibility.TARGET_ONLY and from_inventory_to_owner) or (row.basic_compatibility == PieMenuCategoryCompatibility.FORWARDED_ONLY and not from_inventory_to_owner):
                    continue
                # run tests on resolver
                if not row.tests.run_tests(resolver):
                    continue
                # return new pie menu category
                return row.new_pie_menu_category


@inject_to(ChoiceMenu, '_add_menu_item')
def _edit_choice_menu_categories(original, self, aop, context, result):
    original(self, aop, context, result)
    try:
        menu_item = self.menu_items[aop.aop_id]
        resolver = SingleActorAndObjectResolver(context.sim, aop.target, source='yourmom')
        # check if affordance is forwarded
        from_inventory_to_owner = aop.interaction_parameters is not None and aop.interaction_parameters.get('from_inventory_to_owner', False)
        # get the tested pie menu category
        new_category = TestedPieMenuCategories.get_category(aop.affordance, resolver, from_inventory_to_owner=from_inventory_to_owner)
        # update menu item
        if new_category is not None:
            logger.debug("Updating category: {}: {} -> {}".format(aop.affordance, menu_item.category_key, new_category.guid64))
            menu_item.category_key = new_category.guid64
    except:
        logger.exception("Failed updating pie menu category")
