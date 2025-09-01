from animation.animation_overrides_liability import AnimationOverridesLiability
from buffs.tunable import RemoveBuffLiability
from careers.career_event_liabilities import CareerEventTravelLiability
from crafting.crafting_station_liability import CraftingStationLiability
from interactions.object_liabilities import TemporaryHiddenInventoryTransferLiability
from interactions.object_retrieval_liability import ObjectRetrievalLiability
from interactions.rabbit_hole import HideSimLiability
from interactions.utils.change_clock_speed_liability import ChangeClockSpeedsLiability
from interactions.utils.custom_camera_liability import CustomCameraLiability
from interactions.utils.lighting_liability import LightingLiability
from interactions.utils.route_goal_suppression_liability import RouteGoalSuppressionLiability
from interactions.utils.teleport_liability import TeleportLiability
from interactions.utils.temporary_state_change_liability import TemporaryStateChangeLiability
from interactions.utils.user_cancelable_chain_liability import UserCancelableChainLiability
from interactions.vehicle_liabilities import VehicleLiability
from objects.components.game.game_challenge_liability import GameChallengeLiability
from pets.missing_pets_liability import MissingPetLiability
from postures.proxy_posture_owner_liability import ProxyPostureOwnerLiability
from restaurants.restaurant_liabilities import RestaurantDeliverFoodLiability
from sims.daycare import DaycareLiability
from sims4.tuning.tunable import TunableVariant
from situations.situation_liabilities import CreateSituationLiability, RunningSituationLiability
from interactions.utils.tunable import TimeoutLiability, SaveLockLiability, CriticalPriorityLiability, GameSpeedLiability, PushAffordanceOnRouteFailLiability
from teleport.teleport_type_liability import TeleportStyleLiability
from whims.whims_tracker import HideWhimsLiability
from sims.outfits.outfit_change import ChangeOutfitLiability


class BasicLiabilityVariant(TunableVariant):
    def __init__(self):
        super().__init__(
            timeout=TimeoutLiability.TunableFactory(),
            save_lock=SaveLockLiability.TunableFactory(),
            teleport=TeleportLiability.TunableFactory(),
            lighting=LightingLiability.TunableFactory(),
            crafting_station=CraftingStationLiability.TunableFactory(),
            daycare=DaycareLiability.TunableFactory(),
            critical_priority=CriticalPriorityLiability.TunableFactory(),
            career_event_travel=CareerEventTravelLiability.TunableFactory(),
            game_speed=GameSpeedLiability.TunableFactory(),
            hide_whims=HideWhimsLiability.TunableFactory(),
            remove_buff=RemoveBuffLiability.TunableFactory(),
            push_affordance_on_route_fail=PushAffordanceOnRouteFailLiability.TunableFactory(),
            route_goal_suppression=RouteGoalSuppressionLiability.TunableFactory(),
            outfit_change=ChangeOutfitLiability.TunableFactory(),
            object_retrieval=ObjectRetrievalLiability.TunableFactory(),
            game_challenge_liability=GameChallengeLiability.TunableFactory(),
            restaurant_deliver_food_liability=RestaurantDeliverFoodLiability.TunableFactory(),
            teleport_style_liability=TeleportStyleLiability.TunableFactory(),
            animation_overrides=AnimationOverridesLiability.TunableFactory(),
            hide_sim_liability=HideSimLiability.TunableFactory(),
            user_cancelable_chain=UserCancelableChainLiability.TunableFactory(),
            create_situation=CreateSituationLiability.TunableFactory(),
            running_situation=RunningSituationLiability.TunableFactory(),
            missing_pet=MissingPetLiability.TunableFactory(),
            proxy_posture_owner=ProxyPostureOwnerLiability.TunableFactory(),
            vehicles=VehicleLiability.TunableFactory(),
            temporary_state_change=TemporaryStateChangeLiability.TunableFactory(),
            temporary_hidden_inventory_transfer=TemporaryHiddenInventoryTransferLiability.TunableFactory(),
            enable_custom_camera=CustomCameraLiability.TunableFactory(),
            change_clock_speeds_liability=ChangeClockSpeedsLiability.TunableFactory(),
        )
