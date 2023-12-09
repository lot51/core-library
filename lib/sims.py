from interactions.interaction_finisher import FinishingType
from objects import ALL_HIDDEN_REASONS
from sims.sim import Sim
from sims.sim_info import SimInfo


def get_sim_name(sim_or_sim_info):
    template = '{} {}'
    if isinstance(sim_or_sim_info, SimInfo):
        sim_info = sim_or_sim_info
    elif isinstance(sim_or_sim_info, Sim):
        sim_info = sim_or_sim_info.sim_info
    else:
        return None
    return template.format(sim_info.first_name, sim_info.last_name)


def cancel_all_interactions(sim_or_sim_info, allow_hidden=True, finishing_type=FinishingType.USER_CANCEL, cancel_reason='Canceled via script'):
    if isinstance(sim_or_sim_info, SimInfo):
        sim = sim_or_sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS if allow_hidden else 0)
    else:
        sim = sim_or_sim_info
    if sim is not None:
        for interaction in sim.get_all_running_and_queued_interactions():
            interaction.cancel(finishing_type, cancel_reason_msg=cancel_reason)