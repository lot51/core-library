import services
from lot51_core import logger
from lot51_core.tunables.situation_actions import SituationActionVariant
from lot51_core.tunables.bouncer_request import TunableBouncerRequest
from sims4.tuning.tunable import TunableList, TunableMapping, Tunable, TunableTuple, TunableRange
from situations.create_and_use_object_situation import TARGET_OBJECT_TOKEN
from situations.custom_states.custom_states_situation import CustomStatesSituation



class DefaultObjectCustomStatesSituation(CustomStatesSituation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_object = self._get_target_object()

    def _get_target_object(self):
        reader = self._seed.custom_init_params_reader
        if reader is None:
            target_object_id = self._seed.extra_kwargs.get('default_target_id', None)
        else:
            target_object_id = reader.read_uint64(TARGET_OBJECT_TOKEN, None)
        if target_object_id:
            return services.object_manager().get(target_object_id)

    def get_target_object(self):
        return self.target_object

    def _save_custom_situation(self, writer):
        if self.target_object is not None:
            writer.write_uint64(TARGET_OBJECT_TOKEN, self.target_object.id)
        super()._save_custom_situation(writer)


class AdvancedCustomStatesSituation(DefaultObjectCustomStatesSituation):

    INSTANCE_TUNABLES = {
        'bouncer_requests': TunableMapping(
            description="An alternative to auto_invite defined in the SituationJob.",
            key_name="situation_state",
            key_type=Tunable(tunable_type=str, default=None, allow_empty=False),
            value_type=TunableTuple(
                request=TunableBouncerRequest(),
                count=TunableRange(tunable_type=int, minimum=1, default=1),
            )
        ),
        'job_spawn_actions': TunableList(
            description="Situation actions to apply when a Sim spawns into specific jobs.",
            tunable=SituationActionVariant()
        ),
    }

    __slots__ = ('bouncer_requests', 'job_spawn_actions',)

    def change_state_by_key(self, situation_key, **kwargs):
        super().change_state_by_key(situation_key, **kwargs)
        self._submit_bouncer_requests(situation_key)

    def _submit_bouncer_requests(self, state_name):
        for request_info in self.bouncer_requests.get(state_name, ()):
            for x in range(request_info.count):
                self.manager.bouncer.submit_request(request_info.request)

    def _on_add_sim_to_situation(self, sim, job, *args, **kwargs):
        super()._on_add_sim_to_situation(sim, job, *args, **kwargs)
        try:
            for action in self.job_spawn_actions:
                if action.is_valid(sim, job):
                    action.apply_to_sim(self, sim, job)
        except Exception as e:
            logger.exception("failed to apply job_spawn_actions to sim {}".format(e))
