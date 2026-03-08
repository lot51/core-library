from lot51_core.portals.advanced_teleport import _PortalTypeDataAdvancedTeleport
from routing.portals.portal_data import _Portal
from routing.portals.portal_data_animation import _PortalTypeDataAnimation
from routing.portals.portal_data_build_ladders import _PortalTypeDataBuildLadders
from routing.portals.portal_data_build_ladders_slide import _PortalTypeDataBuildLaddersSlide
from routing.portals.portal_data_dynamic import _PortalTypeDataDynamic
from routing.portals.portal_data_dynamic_stairs import _PortalTypeDataDynamicStairs
from routing.portals.portal_data_elevator import _PortalTypeDataElevator
from routing.portals.portal_data_locomotion import _PortalTypeDataLocomotion
from routing.portals.portal_data_object_ladders import _PortalTypeDataObjectLadders
from routing.portals.portal_data_ocean_ladders import _PortalTypeDataOceanLadders
from routing.portals.portal_data_posture import _PortalTypeDataPosture
from routing.portals.portal_data_stairs import _PortalTypeDataStairs
from routing.portals.portal_data_teleport import _PortalTypeDataTeleport
from routing.portals.portal_data_variable_jump import _PortalTypeDataVariableJump
from sims4.tuning.tunable import TunableVariant
from snippets import define_snippet


class PortalTraversalTypeVariant(TunableVariant):
    def __init__(self, default='locomotion', *args, **kwargs):
        super().__init__(
            *args,
            locomotion=_PortalTypeDataLocomotion.TunableFactory(),
            animation=_PortalTypeDataAnimation.TunableFactory(),
            variable_jump=_PortalTypeDataVariableJump.TunableFactory(),
            dynamic_jump=_PortalTypeDataDynamic.TunableFactory(),
            teleport=_PortalTypeDataTeleport.TunableFactory(),
            posture_change=_PortalTypeDataPosture.TunableFactory(),
            stairs=_PortalTypeDataStairs.TunableFactory(),
            dynamic_stairs=_PortalTypeDataDynamicStairs.TunableFactory(),
            elevator=_PortalTypeDataElevator.TunableFactory(),
            ocean_ladder=_PortalTypeDataOceanLadders.TunableFactory(),
            build_ladder=_PortalTypeDataBuildLadders.TunableFactory(),
            build_ladder_slide=_PortalTypeDataBuildLaddersSlide.TunableFactory(),
            object_ladder=_PortalTypeDataObjectLadders.TunableFactory(),
            **kwargs,
            default=default
        )



class _AdvancedPortalData(_Portal):
    """
    Refer to simulation/portals/portal_data.py for original class
    """

    FACTORY_TUNABLES = {
        'traversal_type': PortalTraversalTypeVariant(
            advanced_teleport=_PortalTypeDataAdvancedTeleport.TunableFactory(),
        ),
    }

TunableAdvancedPortalReference, _ = define_snippet('Core_Lib_Advanced_Portal_Data', _AdvancedPortalData.TunableFactory())
