import services
from interactions.interaction_finisher import FinishingType
from objects import ALL_HIDDEN_REASONS
from protocolbuffers import Consts_pb2
from sims.sim import Sim
from sims.sim_info import SimInfo


def get_sim_info(sim_or_sim_info) -> SimInfo:
    if isinstance(sim_or_sim_info, SimInfo):
        return sim_or_sim_info
    elif isinstance(sim_or_sim_info, Sim):
        return sim_or_sim_info.sim_info


def get_sim_name(sim_or_sim_info):
    template = '{} {}'
    sim_info = get_sim_info(sim_or_sim_info)
    if sim_info is not None:
        return template.format(sim_info.first_name, sim_info.last_name)


def cancel_all_interactions(sim_or_sim_info, allow_hidden=True, finishing_type=FinishingType.USER_CANCEL, cancel_reason='Canceled via script'):
    if isinstance(sim_or_sim_info, SimInfo):
        sim = sim_or_sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS if allow_hidden else 0)
    else:
        sim = sim_or_sim_info
    if sim is not None:
        for interaction in sim.get_all_running_and_queued_interactions():
            interaction.cancel(finishing_type, cancel_reason_msg=cancel_reason)


def debit_money_from_sim(sim_or_sim_info, amount=0, business_zone_id=None, business_funds_category=None, require_full_amount=False):
    sim_info = get_sim_info(sim_or_sim_info)
    if sim_info is None or amount == 0:
        return False
    if business_zone_id is not None:
        business_service = services.business_service()
        business_manager = business_service.get_business_manager_for_zone(business_zone_id)
        if business_manager is not None:
            return business_manager.funds.try_remove(
                amount,
                Consts_pb2.TELEMETRY_OBJECT_BUY,
                sim=sim_info.get_sim_instance(),
                funds_category=business_funds_category,
                require_full_amount=require_full_amount
            )
    else:
        return sim_info.household.funds.try_remove(
            amount,
            Consts_pb2.TELEMETRY_OBJECT_BUY,
            sim=sim_info.get_sim_instance(),
            require_full_amount=require_full_amount
        )
    return False


def credit_money_to_sim(sim_or_sim_info, amount=0, business_zone_id=None, tags=None, count_as_earnings=False):
    sim_info = get_sim_info(sim_or_sim_info)
    if sim_info is None:
        return False
    if business_zone_id is not None:
        business_service = services.business_service()
        business_manager = business_service.get_business_manager_for_zone(business_zone_id)
        if business_manager is not None:
            return business_manager.funds.add(
                amount,
                Consts_pb2.TELEMETRY_OBJECT_BUY,
                sim=sim_info.get_sim_instance(),
                count_as_earnings=count_as_earnings,
            )
    else:
        return sim_info.household.funds.add(
            amount,
            Consts_pb2.TELEMETRY_OBJECT_BUY,
            sim=sim_info.get_sim_instance(),
            tags=tags,
            count_as_earnings=count_as_earnings,
        )
    return False