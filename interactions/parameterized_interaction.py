import element_utils
import sims4.random
from event_testing.resolver import SingleActorAndObjectResolver, DoubleObjectResolver
from interactions import ParticipantType, ParticipantTypeSavedActor
from interactions.aop import AffordanceObjectPair
from interactions.context import InteractionSource, InteractionContext
from interactions.interaction_finisher import FinishingType
from lot51_core import logger
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from services import get_instance_manager
from sims4.localization import TunableLocalizedStringFactory
from sims4.resources import Types
from sims4.utils import flexmethod
from singletons import DEFAULT
from event_testing.results import TestResult
from sims4.tuning.tunable import TunableTuple, TunableReference, TunableList, OptionalTunable, TunableEnumEntry, Tunable
from interactions.base.super_interaction import SuperInteraction


class ParameterizedRequestContinuationMixin:
    INSTANCE_TUNABLES = {
        'paramaterized_autonomy_continuation': OptionalTunable(
            tunable=TunableTuple(
                commodities=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.STATISTIC))
                ),
                static_commodities=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.STATIC_COMMODITY))
                ),
                exclude_static_commodities=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.STATIC_COMMODITY))
                ),
                loot_on_success=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.ACTION))
                ),
                loot_on_failure=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.ACTION))
                ),
                context_source_override=OptionalTunable(tunable=TunableEnumEntry(tunable_type=InteractionSource, default=InteractionSource.AUTONOMY)),
                test_autonomous_availability=Tunable(tunable_type=bool, default=False),
            )
        )
    }

    def _handle_success(self, resolver):
        for loot in self.paramaterized_autonomy_continuation.loot_on_success:
            loot.apply_to_resolver(resolver)

    def _handle_failure(self, resolver):
        for loot in self.paramaterized_autonomy_continuation.loot_on_failure:
            loot.apply_to_resolver(resolver)

    def _run_paramaterized_request(self, obj):
        parameters = self.paramaterized_autonomy_continuation
        static_commodity_list = parameters.static_commodities
        exclude_static_commodity_list = parameters.exclude_static_commodities

        resolver = self.get_resolver(target=obj)
        actor_info = resolver.get_participant(ParticipantType.Actor)
        actor = actor_info.get_sim_instance()
        autonomy_rule = actor.get_off_lot_autonomy_rule()
        obj_available = parameters.test_autonomous_availability is None or actor.autonomy_component.get_autonomous_availability_of_object(obj, autonomy_rule, reference_object=actor)

        if obj_available:
            ctx = self.context.clone_for_continuation(self, source=parameters.context_source_override if parameters.context_source_override is not None else self.context.source, carry_target=self.carry_target)
            potential_aops = list()
            for aop in obj.potential_interactions(ctx):
                try:
                    if ctx.source == InteractionContext.SOURCE_AUTONOMY:
                        if not aop.affordance.allow_autonomous or not aop.affordance.test_autonomous.run_tests(resolver, skip_safe_tests=False, search_for_tooltip=False):
                            # logger.debug("[{}] affordance NOT allowed autonomously {}".format(self, aop.affordance))
                            continue
                        # logger.debug("[{}] affordance allowed autonomously {}".format(self, aop.affordance))

                    execute_result = aop.interaction_factory(ctx)
                    interaction = execute_result.interaction

                    total_desire = 0
                    for sc_data in interaction._static_commodities:
                        if sc_data.static_commodity in static_commodity_list and sc_data.static_commodity not in exclude_static_commodity_list:
                            total_desire += sc_data.desire * sc_data.static_commodity.ad_data

                    if len(parameters.commodities):
                        for stat_op_list in interaction.autonomy_ads_gen(target=obj, include_hidden_false_ads=False):
                            if stat_op_list.is_valid(interaction):
                                stat = actor.get_tracker(stat_op_list.stat).get_statistic(stat_op_list.stat, False)
                                if stat is not None:
                                    logger.debug("Testing stat {}".format(stat.stat_type))
                                    if stat.stat_type in parameters.commodities:
                                        fulfillment_rate = stat_op_list.get_fulfillment_rate(interaction)
                                        scored_value = stat.autonomous_desire * actor.get_score_multiplier(stat.stat_type) * stat.autonomy_weight * fulfillment_rate
                                        logger.debug("Scored value {}".format(scored_value))
                                        total_desire += scored_value

                    if total_desire > 0:
                        test_result = aop.test(ctx)
                        logger.debug("[{}] affordance {}, desire {}, result {}".format(self, interaction, total_desire, test_result))
                        if test_result:
                            potential_aops.append((total_desire, aop))
                except:
                    logger.exception("Failed scoring aop for request: {} -> {}".format(self, aop))

            if len(potential_aops):
                aop_select = sims4.random.weighted_random_item(potential_aops)
                if aop_select is not None:
                    if aop_select.execute(ctx):
                        logger.debug("executed aop {}".format(aop_select))
                        self._handle_success(resolver)
                        return True
                    logger.debug("failed to execute aop {}".format(aop_select))
        logger.debug("no aops found for obj {}".format(obj))
        self._handle_failure(resolver)
        return False


class SpecificInteractionContinuationMixin:
    INSTANCE_TUNABLES = {
        'affordance_continuation': OptionalTunable(
            tunable=TunableReference(manager=get_instance_manager(Types.INTERACTION))
        ),
        'continuation_si_override': OptionalTunable(
           tunable=TunableReference(manager=get_instance_manager(Types.INTERACTION)),
        ),
    }

    def _run_paramaterized_request(self, obj):
        ctx = self.context.clone_for_continuation(self, carry_target=self.carry_target)
        # si = self.continuation_si_override if self.continuation_si_override is not None else self.affordance_continuation
        aop = AffordanceObjectPair(self.affordance_continuation, obj, self.affordance_continuation, None, saved_participants=self._saved_participants)
        (test_result, execute_result) = aop.test_and_execute(ctx)
        logger.debug("specific aop result: {}, {}".format(test_result, execute_result))
        return bool(test_result)


class BaseParameterizedSuperInteraction(SuperInteraction):
    INSTANCE_TUNABLES = {
        'object_source': ObjectSearchMethodVariant(),
        'object_source_fail_tooltip': OptionalTunable(
            tunable=TunableLocalizedStringFactory(),
        )
    }

    @flexmethod
    def test(cls, inst, context=DEFAULT, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        original_result = super(__class__, inst_or_cls).test(context=context, **kwargs)
        if not bool(original_result):
            return original_result

        try:
            # logger.debug("Testing interaction {}".format(inst_or_cls))
            resolver = inst_or_cls.get_resolver(context=context, **kwargs)
            for obj in inst_or_cls.object_source.get_objects_gen(resolver=resolver, log_results=False):
                return TestResult.TRUE
            return TestResult(False, 'No objects found', tooltip=inst_or_cls.object_source_fail_tooltip)
        except:
            logger.exception("Failed during param interaction test")
            return original_result

    def _perform_paramaterized_request_gen(self, timeline):
        resolver = self.get_resolver()
        # logger.debug("Running interaction {}".format(self))
        for chosen_obj in self.object_source.get_objects_gen(resolver=resolver, log_results=False):
            if self._run_paramaterized_request(chosen_obj):
                return True
        self.cancel(FinishingType.TRANSITION_FAILURE, cancel_reason_msg="Failed to push continuation")
        return False

    def _build_outcome_sequence(self, *args, **kwargs):
        sequence = super()._build_outcome_sequence(*args, **kwargs)
        return element_utils.build_critical_section(sequence, self._perform_paramaterized_request_gen)


class ParameterizedSpecificSuperInteraction(BaseParameterizedSuperInteraction, SpecificInteractionContinuationMixin):
    pass


class ParameterizedSuperInteraction(BaseParameterizedSuperInteraction, ParameterizedRequestContinuationMixin):
    pass
