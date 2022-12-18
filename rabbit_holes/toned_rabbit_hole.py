import alarms
import clock
import services
import random
from away_actions.away_actions import AwayAction
from away_actions.away_actions_interactions import ApplyAwayActionInteraction
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet
from interactions.aop import AffordanceObjectPair
from lot51_core import logger
from lot51_core.utils.injection import inject_to
from rabbit_hole.rabbit_hole import RabbitHole
from services import get_instance_manager
from services.rabbit_hole_service import RabbitHoleService
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableTuple, Tunable, TunableSimMinute


class RabbitHoleTone(AwayAction):

    INSTANCE_TUNABLES = {
        'periodic_loot': TunableList(
            tunable=TunableReference(manager=get_instance_manager(Types.ACTION))
        ),
        'periodic_loot_minutes': TunableSimMinute(default=15),
        'trigger_loot_on_stop': Tunable(tunable_type=bool, default=True)
    }

    __slots__ = ('periodic_loot', 'periodic_loot_minutes', 'trigger_loot_on_stop')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_alarm_handle = None
        self._last_update_time = None

    def run(self, callback):
        super().run(callback)
        self._last_update_time = services.time_service().sim_now
        time_span = clock.interval_in_sim_minutes(self.periodic_loot_minutes)
        self._update_alarm_handle = alarms.add_alarm(self, time_span, lambda alarm_handle: self._update(), repeating=True)

    def stop(self):
        if self._update_alarm_handle is not None:
            alarms.cancel_alarm(self._update_alarm_handle)
            self._update_alarm_handle = None
        if self.trigger_loot_on_stop:
            self._update()
        super().stop()

    def _update(self):
        now = services.time_service().sim_now
        elapsed = now - self._last_update_time
        self._last_update_time = now
        resolver = self.get_resolver()
        for loot in self.periodic_loot:
            loot.apply_to_resolver(resolver)


class TonedRabbitHole(RabbitHole):
    REMOVE_INSTANCE_TUNABLES = ('away_action',)

    INSTANCE_TUNABLES = {
        'allow_leave_early': Tunable(tunable_type=bool, default=True),
        'additional_affordances': TunableList(
            description="Additional interactions that are available in the rabbit hole pie menu.",
            tunable=TunableReference(
                manager=get_instance_manager(Types.INTERACTION)
            ),
        ),
        'tone_interaction': TunableReference(
            description="The default interaction to trigger Tones/Away Actions",
            manager=get_instance_manager(Types.INTERACTION),
            class_restrictions=(ApplyAwayActionInteraction,),
        ),
        'default_tones': TunableList(
            description="A list of possible Away Actions to choose as the default when activating this rabbit hole. Does not have to be listed in 'tones' below.",
            tunable=TunableTuple(
                away_action=TunableReference(
                    manager=get_instance_manager(Types.AWAY_ACTION)
                ),
                tests=TunableTestSet(),
            )
        ),
        'tones': TunableList(
            description="A list of possible Away Actions to display in the rabbit hole pie menu.",
            tunable=TunableTuple(
                away_action=TunableReference(
                    manager=get_instance_manager(Types.AWAY_ACTION)
                ),
                tests=TunableTestSet(),
            )
        ),
    }

    __slots__ = ('allow_leave_early', 'additional_affordances', 'tone_interaction', 'default_tones', 'tones')

    def get_resolver(self):
        sim_info = services.sim_info_manager().get(self.sim_id)
        return SingleSimResolver(sim_info)

    def get_available_tones_gen(self, resolver):
        if self.tones is not None:
            for tone in self.tones:
                if tone.away_action is not None:
                    if tone.tests.run_tests(resolver):
                        yield tone.away_action

    def get_default_tone(self):
        resolver = self.get_resolver()
        possible_tones = list()
        for tone in self.default_tones:
            if tone.away_action is not None:
                if tone.tests.run_tests(resolver):
                    possible_tones.append(tone.away_action)

        if possible_tones is None:
            return None

        return random.choice(possible_tones)

    def on_activate(self):
        super().on_activate()
        try:
            tracker = self.sim.away_action_tracker
            tone = self.get_default_tone()
            if tracker and tone:
                tracker.create_and_apply_away_action(tone)
            else:
                logger.warn("Failed to find select default tone for rabbit hole: {}".format(self))
        except:
            logger.exception("failed on rabbithole activate")

    def _is_valid_tone(self, tone, resolver):
        for other_tone in self.get_available_tones_gen(resolver):
            if tone.guid64 == other_tone.guid64:
                return True
        return False

    def get_away_action_aops_gen(self, sim_info, context, **kwargs):
        try:
            resolver = SingleSimResolver(sim_info)
            for tone in self.get_available_tones_gen(resolver):
                yield AffordanceObjectPair(
                    self.tone_interaction,
                    None,
                    self.tone_interaction,
                    None,
                    away_action=tone,
                    away_action_sim_info=sim_info,
                    **kwargs,
                )

            for affordance in self.additional_affordances:
                for aop in affordance.potential_interactions(None, context, sim_info=sim_info, **kwargs):
                    yield aop

            if self.allow_leave_early:
                for aop in services.get_rabbit_hole_service().LEAVE_EARLY_INTERACTION.potential_interactions(None, context, sim_info=sim_info, **kwargs):
                    yield aop
        except:
            logger.exception("failed generating rabbithole aops")


@inject_to(RabbitHoleService, 'sim_skewer_rabbit_hole_affordances_gen')
def _sim_skewer_rabbit_hole_affordances_gen(original, self, sim_info, context, *args, **kwargs):
    rabbit_hole_id = self.get_head_rabbit_hole_id(sim_info.sim_id)
    rabbit_hole = self._get_rabbit_hole(sim_info.sim_id, rabbit_hole_id)
    if isinstance(rabbit_hole, TonedRabbitHole):
        yield from rabbit_hole.get_away_action_aops_gen(sim_info, context, **kwargs)
    else:
        yield from original(self, sim_info, context, *args, **kwargs)