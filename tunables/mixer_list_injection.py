import services
from interactions.social.social_mixer_interaction import SocialMixerInteraction
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableList


class TunableMixerListInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'mixer_list': TunableReference(manager=services.get_instance_manager(Types.SNIPPET)),
        'mixers': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), class_restrictions=(SocialMixerInteraction,)),
        )
    }

    __slots__ = ('mixer_list', 'mixers',)

    def inject(self):
        if self.mixer_list is not None:
            mixers_to_add = list()
            for mixer in self.mixers:
                if mixer is not None:
                    mixers_to_add.append(mixer)
            self.mixer_list.value += tuple(mixers_to_add)