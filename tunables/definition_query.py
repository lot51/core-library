import services
from crafting.recipe_helpers import get_recipes_matching_tag
from event_testing.tests import TunableTestSet
from lot51_core.tunables.object_query import ObjectFilterRandomSingleChoice, ObjectFilterRandomMultipleChoice
from lot51_core.utils.collections import AttributeDict
from sims4.resources import Types, get_resource_key
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableVariant, TunableList, TunableReference, Tunable, TunableEnumSet
from tag import Tag


class DefinitionData(AttributeDict):
    __slots__ = ('definition', 'icon_override', 'recipe', 'quality',)


class DefinitionFilterVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, random_single_choice=ObjectFilterRandomSingleChoice.TunableFactory(), random_multiple_choice=ObjectFilterRandomMultipleChoice.TunableFactory(), **kwargs)



class BaseDefinitionSource(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'filter': DefinitionFilterVariant(),
        'tests': TunableTestSet(),
    }

    __slots__ = ('tests', 'filter',)

    def _get_definitions_gen(self, resolver=None):
        raise NotImplementedError

    def _get_filtered_gen(self, def_list):
        if self.filter is not None:
            yield from self.filter.filter_objects_gen(def_list)
        else:
            yield from def_list

    def _get_definition_data_gen(self, resolver=None):
        for definition in self._get_definitions_gen(resolver=resolver):
            yield DefinitionData({"definition": definition})

    def get_definitions_gen(self, resolver=None):
        if self.tests.run_tests(resolver):
            all_definitions = self._get_definitions_gen(resolver=resolver)
            filtered_definitions = self._get_filtered_gen(all_definitions)
            yield from filtered_definitions

    def get_definition_data_gen(self, resolver=None):
        if self.tests.run_tests(resolver):
            all_definitions = self._get_definition_data_gen(resolver=resolver)
            filtered_definitions = self._get_filtered_gen(all_definitions)
            yield from filtered_definitions


class TaggedRecipesSource(BaseDefinitionSource):
    FACTORY_TUNABLES = {
        'tags': TunableEnumSet(enum_type=Tag, invalid_enums=(Tag.INVALID,)),
    }

    __slots__ = ('tags',)

    def _get_definitions_gen(self, resolver=None):
        for tag in self.tags:
            for recipe in get_recipes_matching_tag(tag):
                if hasattr(recipe, 'has_final_product_definition') and recipe.recipe_tags is not None:
                    yield recipe.final_product_definition

    def _get_definition_data_gen(self, resolver=None):
        for tag in self.tags:
            for recipe in get_recipes_matching_tag(tag):
                if hasattr(recipe, 'has_final_product_definition') and recipe.recipe_tags is not None:
                    yield DefinitionData({"definition": recipe.final_product_definition, "recipe": recipe})


class SpecificRecipesSource(BaseDefinitionSource):
    FACTORY_TUNABLES = {
        'recipes': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.RECIPE)))
    }

    __slots__ = ('recipes',)

    def _get_definitions_gen(self, resolver=None):
        for recipe in self.recipes:
            if recipe is not None and recipe.has_final_product_definition:
                yield recipe.final_product_definition

    def _get_definition_data_gen(self, resolver=None):
        for recipe in self.recipes:
            if recipe is not None and recipe.has_final_product_definition:
                yield DefinitionData({"definition": recipe.final_product_definition, "recipe": recipe})


class SpecificDefinitionsSource(BaseDefinitionSource):
    FACTORY_TUNABLES = {
        'definitions': TunableList(tunable=TunableReference(manager=services.definition_manager()))
    }

    __slots__ = ('definitions',)

    def _get_definitions_gen(self, resolver=None):
        for definition in self.definitions:
            if definition is not None:
                yield definition


class TaggedDefinitionsSource(BaseDefinitionSource):
    FACTORY_TUNABLES = {
        'tags': TunableEnumSet(enum_type=Tag, invalid_enums=(Tag.INVALID,)),
    }

    __slots__ = ('tags',)

    def _get_definitions_gen(self, resolver=None):
        for definition in services.definition_manager().get_definitions_for_tags_gen(self.tags):
            yield definition


class ObjectTuningSource(BaseDefinitionSource):
    FACTORY_TUNABLES = {
        'objects': TunableList(tunable=Tunable(tunable_type=int, default=0))
    }

    __slots__ = ('objects',)

    def _get_definitions_gen(self, resolver=None):
        _yield_cache = set()
        for tuning_id in self.objects:
            tuning = services.get_instance_manager(Types.OBJECT).types.get(get_resource_key(tuning_id, Types.OBJECT))
            if tuning is not None and tuning.definition not in _yield_cache:
                _yield_cache.add(tuning.definition)
                yield tuning.definition


class DefinitionSearchMethodVariant(TunableVariant):

    VARIANT_OPTIONS = {
        'object_tuning': ObjectTuningSource.TunableFactory(),
        'specific_definitions': SpecificDefinitionsSource.TunableFactory(),
        'specific_recipes': SpecificRecipesSource.TunableFactory(),
        'tagged_definitions': TaggedDefinitionsSource.TunableFactory(),
        'tagged_recipes': TaggedRecipesSource.TunableFactory(),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **self.VARIANT_OPTIONS, default='specific_definitions', **kwargs)