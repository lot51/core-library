import services
import random
from lot51_core import logger
from event_testing.tests import TunableTestSet
from event_testing.resolver import SingleObjectResolver
from interactions import ParticipantType
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableInterval, Tunable, TunableVariant, TunableEnumSet, TunableEnumEntry
from tag import Tag
from objects.components.types import INVENTORY_COMPONENT


class ObjectFilterRandomSingleChoice(HasTunableSingletonFactory, AutoFactoryInit):

    def filter_objects(self, obj_list=()):
        _obj_list = list(obj_list)
        logger.debug("getting random single choice: {}".format(_obj_list))
        if len(_obj_list) == 0:
            return []
        yield random.choice(_obj_list)


class ObjectFilterRandomMultipleChoice(HasTunableSingletonFactory, AutoFactoryInit):

    FACTORY_TUNABLES = {
        'limit': TunableInterval(tunable_type=int, default_lower=1, default_upper=1, minimum=0)
    }

    __slots__ = ('limit',)

    def filter_objects(self, obj_list=()):
        _obj_list = list(obj_list)
        logger.debug("getting random multiple choice: {}".format(_obj_list))
        if len(_obj_list) == 0:
            return []
        num_choices = random.randint(self.limit.lower_bound, min(len(_obj_list), self.limit.upper_bound))
        yield from random.sample(_obj_list, num_choices)


class ObjectFilterVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, random_single_choice=ObjectFilterRandomSingleChoice.TunableFactory(), random_multiple_choice=ObjectFilterRandomMultipleChoice.TunableFactory(), **kwargs)


class _GetObjectsBase(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'filter': ObjectFilterVariant(),
        'additional_tests': TunableTestSet(),
    }

    __slots__ = ('filter', 'additional_tests',)

    def _get_filtered_objects(self, obj_list):
        if self.filter is not None:
            yield from self.filter.filter_objects(obj_list)
        else:
            yield from obj_list

    def _get_objects_gen(self, resolver=None):
        yield from []

    def get_objects_gen(self, resolver=None):
        obj_list = self._get_objects_gen(resolver)
        yield from self._get_filtered_objects(obj_list)


class GetObjectsFromInventory(_GetObjectsBase):
    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(tunable_type=ParticipantType, default=ParticipantType.Actor),
        'hidden': Tunable(tunable_type=bool, default=False)
    }

    __slots__ = ('subject', 'hidden',)

    def get_inventory(self, resolver):
        if resolver is not None:
            subject = resolver.get_participant(self.subject)
            return subject.get_sim_instance().get_component(INVENTORY_COMPONENT)


    def _get_objects_gen(self, resolver=None):
        inventory = self.get_inventory(resolver)
        if inventory is not None:
            for obj in inventory._storage:
                if self.hidden and not inventory.is_object_hidden(obj):
                    continue
                resolver = SingleObjectResolver(obj)
                if self.additional_tests.run_tests(resolver):
                    yield obj


class GetObjectsOnActiveLot(_GetObjectsBase):

    def _get_objects_gen(self, resolver=None):
        for obj in services.object_manager().get_objects_with_tags_gen(*self.tags):
            if obj.is_on_active_lot():
                resolver = SingleObjectResolver(obj)
                if self.additional_tests.run_tests(resolver):
                    yield obj


class GetObjectsByTags(_GetObjectsBase):
    FACTORY_TUNABLES = {
        'tags': TunableEnumSet(Tag, enum_default=Tag.INVALID, invalid_enums=(Tag.INVALID,)),
    }

    __slots__ = ('tags',)

    def _get_objects_gen(self, resolver=None):
        for obj in services.object_manager().get_objects_with_tags_gen(*self.tags):
            resolver = SingleObjectResolver(obj)
            if self.additional_tests.run_tests(resolver):
                yield obj


class GetObjectsByTuning(_GetObjectsBase):
    FACTORY_TUNABLES = {
        'tuning_id': Tunable(tunable_type=int, default=0),
    }

    __slots__ = ('tuning_id',)

    def _get_objects_gen(self, resolver=None):
        for obj in services.object_manager().valid_objects():
            if hasattr(obj, 'guid64') and obj.guid64 == self.tuning_id:
                resolver = SingleObjectResolver(obj)
                if self.additional_tests.run_tests(resolver):
                    yield obj


class GetObjectsByDefinition(_GetObjectsBase):
    FACTORY_TUNABLES = {
        'definition_id': Tunable(tunable_type=int, default=0),
    }

    __slots__ = ('definition_id',)

    def _get_objects_gen(self, resolver=None):
        for obj in services.object_manager().valid_objects():
            if hasattr(obj, 'definition') and obj.definition.id == self.definition_id:
                resolver = SingleObjectResolver(obj)
                if self.additional_tests.run_tests(resolver):
                    yield obj


class ObjectSearchMethodVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, tags=GetObjectsByTags.TunableFactory(), definition=GetObjectsByDefinition.TunableFactory(), tuning=GetObjectsByTuning.TunableFactory(), active_lot=GetObjectsOnActiveLot.TunableFactory(), inventory=GetObjectsFromInventory.TunableFactory(), **kwargs)
