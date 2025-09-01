import services
from sims4.resources import Types
from sims4.tuning.tunable import TunableFactory, TunableReference, TunableEnumEntry, TunableEnumSet
from situations.base_situation import _RequestUserData
from situations.bouncer.bouncer_request import BouncerRequest
from situations.bouncer.bouncer_types import BouncerRequestPriority, RequestSpawningOption
from situations.situation_types import SituationCommonBlacklistCategory


class TunableBouncerRequest(TunableFactory):

    @staticmethod
    def factory(situation, job_type, request_priority, common_blacklist_categories, spawning_option):
        return BouncerRequest(
            situation,
            callback_data=_RequestUserData(),
            job_type=job_type,
            request_priority=request_priority,
            user_facing=situation.is_user_facing,
            exclusivity=situation.exclusivity,
            common_blacklist_categories=common_blacklist_categories,
            spawning_option=spawning_option,
            accept_looking_for_more_work=job_type.accept_looking_for_more_work
        )

    FACTORY_TYPE = factory

    def __init__(self, **kwargs):
        super().__init__(
            job_type=TunableReference(manager=services.get_instance_manager(Types.SITUATION_JOB)),
            request_priority=TunableEnumEntry(tunable_type=BouncerRequestPriority, default=BouncerRequestPriority.EVENT_DEFAULT_JOB),
            common_blacklist_categories=TunableEnumSet(enum_type=SituationCommonBlacklistCategory),
            spawning_option=TunableEnumEntry(tunable_type=RequestSpawningOption, default=RequestSpawningOption.MUST_SPAWN),
            **kwargs
            )
