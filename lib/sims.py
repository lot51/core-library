import services
from interactions.interaction_finisher import FinishingType
from objects import ALL_HIDDEN_REASONS
from protocolbuffers import Consts_pb2
from sims.occult.occult_enums import OccultType
from sims.sim import Sim
from sims.sim_info import SimInfo


def get_sim_info(sim_or_sim_info) -> SimInfo:
    if isinstance(sim_or_sim_info, SimInfo):
        return sim_or_sim_info
    elif isinstance(sim_or_sim_info, Sim):
        return sim_or_sim_info.sim_info


def get_sim_instance(sim_or_sim_info, allow_hidden_flags=0) -> Sim:
    if isinstance(sim_or_sim_info, SimInfo):
        return sim_or_sim_info.get_sim_instance(allow_hidden_flags=allow_hidden_flags)
    elif isinstance(sim_or_sim_info, Sim):
        return sim_or_sim_info


def get_sim_name(sim_or_sim_info):
    template = '{} {}'
    sim_info = get_sim_info(sim_or_sim_info)
    if sim_info is not None:
        return template.format(sim_info.first_name, sim_info.last_name)


def get_occult_sim_info(sim_or_sim_info, occult_type):
    """
    Get the sim info that holds the appearance for a sim by occult type
    """
    sim_info = get_sim_info(sim_or_sim_info)
    if occult_type == OccultType.HUMAN:
        return sim_info
    if sim_info is not None and sim_info.occult_tracker is not None:
        return sim_info.occult_tracker.get_occult_sim_info(occult_type)
    return sim_info

def get_sim_occult_types(sim_or_sim_info):
    """
    Returns all the occult types that the sim has for gameplay purposes.
    If you need the occult type that the sim is presenting as visually, see `get_sim_active_occult_type()`
    """
    sim_info = get_sim_info(sim_or_sim_info)
    if sim_info is None:
        return set()
    return set(filter(lambda v: sim_info.occult_types & v, OccultType))


def get_sim_active_occult_type(sim_or_sim_info):
    """
    Represents the occult type that the sim is presenting as visually

    :return: OccultType
    """
    sim_info = get_sim_info(sim_or_sim_info)
    if sim_info is not None and sim_info.occult_tracker is not None:
        return sim_info.occult_tracker.get_current_occult_types()


def get_occult_sim_infos_gen(sim_or_sim_info, exclude_human=True):
    """
    Get all sim infos for occult types the sim has, excludes the human sim info by default
    """
    sim_info = get_sim_info(sim_or_sim_info)
    if sim_info is not None:
        if not exclude_human:
            yield sim_info
        for occult_type in get_sim_occult_types(sim_info):
            if occult_type == OccultType.HUMAN:
                continue
            occult_sim_info = get_occult_sim_info(sim_info, occult_type)
            if occult_sim_info is not None:
                yield occult_sim_info


def cancel_all_interactions(sim_or_sim_info, allow_hidden=True, finishing_type=FinishingType.USER_CANCEL, cancel_reason='Canceled via script'):
    sim = get_sim_instance(sim_or_sim_info, allow_hidden_flags=ALL_HIDDEN_REASONS if allow_hidden else 0)
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