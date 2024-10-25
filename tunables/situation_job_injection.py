from filters.location_based_filter_terms import TunableLocationBasedFilterTermsSnippet
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple, Tunable, OptionalTunable, TunableEnumEntry
from situations.situation_job import SituationJob
from situations.situation_types import JobHolderNoShowAction
from world.spawn_actions import TunableSpawnActionVariant


class TunableSituationJobInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'situation_jobs': TunableList(
            tunable=TunableReference(manager=get_instance_manager(Types.SITUATION_JOB), pack_safe=True),
        ),
        'additional_location_based_filter_terms': TunableList(
            tunable=TunableLocationBasedFilterTermsSnippet(pack_safe=True)
        ),
        'died_or_left_action_override': OptionalTunable(
            tunable=TunableEnumEntry(JobHolderNoShowAction, default=JobHolderNoShowAction.DO_NOTHING)
        ),
        'no_show_action_override': OptionalTunable(
            tunable=TunableEnumEntry(JobHolderNoShowAction, default=JobHolderNoShowAction.DO_NOTHING)
        ),
        'spawn_action_override': OptionalTunable(
            description="If enabled, this spawn action will be set as the default sim_spawn_action in the job tuning.",
            tunable=TunableSpawnActionVariant(list_pack_safe=True)
        ),
        'alternative_spawn_behaviors': TunableList(
            description="Alternative Spawn Behaviors are originally defined in the SituationJob module tuning. When a Sim spawns into the world with one of the whitelisted jobs, there is a 50 percent chance an alternative spawn action is chosen over the default sim_spawn_action defined in the job tuning.",
            tunable=TunableTuple(
                spawn_action=TunableSpawnActionVariant(list_pack_safe=True),
                weight=Tunable(tunable_type=float, default=1)
            )
        )
    }

    __slots__ = ('situation_jobs', 'additional_location_based_filter_terms', 'died_or_left_action_override', 'no_show_action_override', 'spawn_action_override', 'alternative_spawn_behaviors',)

    def inject(self):
        for job in self.situation_jobs:
            # Override default spawn action
            if self.spawn_action_override is not None:
                job.sim_spawn_action = self.spawn_action_override

            if self.additional_location_based_filter_terms is not None:
                inject_list(job, 'location_based_filter_terms', self.additional_location_based_filter_terms)

            if self.died_or_left_action_override is not None:
                job.died_or_left_action = self.died_or_left_action_override

            if self.no_show_action_override is not None:
                job.no_show_action = self.no_show_action_override

            # Append alternative spawn behaviors to the job cache
            if len(self.alternative_spawn_behaviors):
                if job not in SituationJob._job_to_weighted_spawn_action_list:
                     SituationJob._job_to_weighted_spawn_action_list[job] = []

                weighted_spawn_action_list = SituationJob._job_to_weighted_spawn_action_list[job]
                for action in self.alternative_spawn_behaviors:
                    weighted_action = (action.weight, action.spawn_action,)
                    weighted_spawn_action_list.append(weighted_action)