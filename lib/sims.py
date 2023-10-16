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