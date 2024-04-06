import services
from away_actions.away_actions import AwayAction
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_mapping_lists, inject_dict
from sims.sim_info import SimInfo
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableMapping
from statistics.commodity import Commodity


class TunableSimInfoInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'away_actions': TunableMapping(
            description='A mapping between affordances and lists of away actions.  The affordances are used to generate AoPs with each of the away actions.',
            key_type=TunableReference(
                description='The interaction that will be used to create AoPs from the away list of away actions that it is mapped to.',
                manager=services.get_instance_manager(Types.INTERACTION)
            ),
            value_type=TunableList(
                description='A list of away actions that are available for the player to select from and apply to the sim.',
                tunable=AwayAction.TunableReference(pack_safe=True)
            )
        ),
        'default_away_action': TunableMapping(
            description='Map of commodities to away action.  When the default away action is asked for we look at the ad data of each commodity and select the away action linked to the commodity that is advertising the highest. ',
            key_type=Commodity.TunableReference(description='The commodity that we will look at the advertising value for.', pack_safe=True),
            value_type=AwayAction.TunableReference(description='The away action that will applied if the key is the highest advertising commodity of the ones listed.', pack_safe=True)
        )

    }

    __slots__ = ('away_actions', 'default_away_action')

    def inject(self):
        inject_mapping_lists(SimInfo, 'AWAY_ACTIONS', self.away_actions)
        inject_dict(SimInfo, 'DEFAULT_AWAY_ACTION', new_items=self.default_away_action)
