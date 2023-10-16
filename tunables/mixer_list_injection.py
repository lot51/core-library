import services
from interactions.base.mixer_interaction import MixerInteraction
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList
from snippets import TunableAffordanceListReference


class TunableMixerListInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'mixer_list': TunableAffordanceListReference(),
        'mixers': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION)),
        )
    }

    __slots__ = ('mixer_list', 'mixers',)

    def inject(self):
        if self.mixer_list is not None:
            mixers_to_add = list()
            for mixer in self.mixers:
                # Check if subclass instead of using strict class_restrictions in TunableReference
                # to allow modded subclasses
                if mixer is not None:
                    if not issubclass(mixer, MixerInteraction):
                        logger.error("Class does not extend SocialMixerInteraction: {}, skipping in mixer list injection to {}".format(mixer, self.mixer_list))
                        continue
                    mixers_to_add.append(mixer)
            self.mixer_list.value += tuple(mixers_to_add)
