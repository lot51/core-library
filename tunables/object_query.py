import services
import random
import sims4.random
from lot51_core import logger
from event_testing.tests import TunableTestSet
from event_testing.resolver import SingleObjectResolver
from interactions import ParticipantType
from objects.components.types import INVENTORY_COMPONENT
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableInterval, Tunable, TunableVariant, TunableEnumSet, TunableEnumEntry, TunableReference
from tag import Tag


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

    def get_closest_object(self, relative_position, relative_level, resolver=None):
        object_list = list(self.get_objects_gen(resolver=resolver))
        weights = []
        for obj in object_list:
            delta = obj.position - relative_position
            base_weight = delta.magnitude()
            # score objects on different levels as further away
            if obj.level != relative_level:
                base_weight *= 2

            weight = 10/base_weight
            if obj.parts:
                for part in obj.parts:
                    weights.append((weight, part))
            else:
                weights.append((weight, obj))

        return sims4.random.weighted_random_item(weights)


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
                if (self.hidden and not inventory.is_object_hidden(obj)) or (not self.hidden and inventory.is_object_hidden(obj)):
                    continue
                resolver = SingleObjectResolver(obj)
                if self.additional_tests.run_tests(resolver):
                    yield obj


class GetSituationTargetObject(_GetObjectsBase):
    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(tunable_type=ParticipantType, default=ParticipantType.Actor),
        'situation': TunableReference(manager=services.get_instance_manager(Types.SITUATION)),
    }

    __slots__ = ('subject', 'situation')

    def _get_objects_gen(self, resolver=None):
        situation_manager = services.get_zone_situation_manager()
        if resolver is not None:
            sim_info = resolver.get_participant(self.subject)
            if sim_info and sim_info.is_sim:
                sim = sim_info.get_sim_instance()
                for situation in situation_manager.get_situations_sim_is_in(sim):
                    if situation.guid64 == self.situation.guid64:
                        if hasattr(situation, 'get_target_object'):
                            yield situation.get_target_object()


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
        super().__init__(*args, tags=GetObjectsByTags.TunableFactory(), definition=GetObjectsByDefinition.TunableFactory(), tuning=GetObjectsByTuning.TunableFactory(), active_lot=GetObjectsOnActiveLot.TunableFactory(), inventory=GetObjectsFromInventory.TunableFactory(), situation_target=GetSituationTargetObject.TunableFactory(), **kwargs)
