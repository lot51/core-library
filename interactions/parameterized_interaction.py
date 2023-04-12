from lot51_core import logger
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from services import get_instance_manager
from sims4.resources import Types
from sims4.utils import flexmethod
from singletons import DEFAULT
from event_testing.results import TestResult
from sims4.tuning.tunable import TunableTuple, TunableReference, TunableList, OptionalTunable
from interactions.base.super_interaction import SuperInteraction


class ParameterizedRequestContinuationMixin:
    INSTANCE_TUNABLES = {
        'paramaterized_autonomy_continuation': OptionalTunable(
            tunable=TunableTuple(
                static_commodities=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.STATIC_COMMODITY))
                ),
                loot_on_success=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.ACTION))
                ),
                loot_on_failure=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.ACTION))
                ),
            )
        )
    }

    def _run_paramaterized_request(self, obj):
        static_commodity_list = self.paramaterized_autonomy_continuation.static_commodities

        ctx = self.context.clone_for_continuation(self)
        aop_result = None
        for aop in obj.potential_interactions(ctx):
            sc_result = any(sc.static_commodity in static_commodity_list for sc in aop.affordance._static_commodities)
            if sc_result:
                aop_result = aop.test_and_execute(ctx)
                if aop_result:
                    resolver = self.get_resolver()
                    for loot in self.paramaterized_autonomy_continuation.loot_on_success:
                        loot.apply_to_resolver(resolver)
                    break
        if not aop_result:
            for loot in self.paramaterized_autonomy_continuation.loot_on_failure:
                loot.apply_to_resolver(resolver)


class SpecificInteractionContinuationMixin:
    INSTANCE_TUNABLES = {
        'affordance_continuation': OptionalTunable(
            tunable=TunableReference(manager=get_instance_manager(Types.INTERACTION))
        )
    }

    def _run_paramaterized_request(self, obj):
        ctx = self.context.clone_for_continuation(self)
        for aop in self.affordance_continuation.potential_interactions(obj, ctx):
            aop_result = aop.test_and_execute(ctx)
            if aop_result:
                return aop_result
        return False


class ParameterizedSpecificSuperInteraction(SuperInteraction, SpecificInteractionContinuationMixin):
    INSTANCE_TUNABLES = {
        'object_source': ObjectSearchMethodVariant(),
    }

    @flexmethod
    def test(cls, inst, context=DEFAULT, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        original_result = super(__class__, inst_or_cls).test(context=context, **kwargs)
        if not bool(original_result):
            return original_result

        try:
            resolver = inst_or_cls.get_resolver(context=context, **kwargs)
            for obj in inst_or_cls.object_source.get_objects_gen(resolver=resolver):
                return original_result
            return TestResult(False, 'No objects found')
        except:
            logger.exception("Failed during param interaction test")
            return original_result

    def _run_interaction_gen(self, timeline):
        try:
            resolver = self.get_resolver()
            for chosen_obj in self.object_source.get_objects_gen(resolver=resolver):
                if self._run_paramaterized_request(chosen_obj):
                    break
        except:
            logger.exception("param request failed")
        super()._run_interaction_gen(timeline)


class ParameterizedSuperInteraction(SuperInteraction, ParameterizedRequestContinuationMixin):
    INSTANCE_TUNABLES = {
        'object_source': ObjectSearchMethodVariant(),
    }

    @flexmethod
    def test(cls, inst, context=DEFAULT, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        original_result = super(__class__, inst_or_cls).test(context=context, **kwargs)
        if not bool(original_result):
            return original_result

        try:
            resolver = inst_or_cls.get_resolver(context=context, **kwargs)
            for obj in inst_or_cls.object_source.get_objects_gen(resolver=resolver):
                return original_result
            return TestResult(False, 'No objects found')
        except:
            logger.exception("Failed during param interaction test")
            return original_result

    def _run_interaction_gen(self, timeline):
        try:
            resolver = self.get_resolver()
            for chosen_obj in self.object_source.get_objects_gen(resolver=resolver):
                if self._run_paramaterized_request(chosen_obj):
                    break
        except:
            logger.exception("param request failed")
        super()._run_interaction_gen(timeline)
