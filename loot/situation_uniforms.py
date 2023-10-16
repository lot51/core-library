import services
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core import logger
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from sims4.resources import Types
from sims4.tuning.tunable import OptionalTunable, TunableReference


class ReapplyJobUniformLoot(BaseLootOperation):
    FACTORY_TUNABLES = {
        'situation': OptionalTunable(
            description="Require target sims to be in a specific situation",
            tunable=TunableReference(manager=services.get_instance_manager(Types.SITUATION))
        ),
        'object_source': ObjectSearchMethodVariant(),
    }

    def __init__(self, object_source=None, situation=None, **kwargs):
        self._object_source = object_source
        self._situation = situation
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        for sim in self._object_source.get_objects_gen(resolver=resolver):
            if not sim.is_sim or sim.is_hidden():
                continue
            logger.debug("applying situation uniform for sim {}".format(sim))
            situations = services.get_zone_situation_manager().get_situations_sim_is_in(sim)
            for situation in situations:
                if self._situation is not None and self._situation.guid64 != situation.guid64:
                    continue
                logger.debug("found situation {}".format(situation))
                job_type = situation.get_current_job_for_sim(sim)
                if job_type and job_type.job_uniform is not None:
                    logger.debug("found job {}".format(job_type))
                    situation.set_job_uniform(sim, job_type)
                    break
