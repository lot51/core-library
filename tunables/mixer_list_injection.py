import services
from interactions.base.mixer_interaction import MixerInteraction
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList
from snippets import TunableAffordanceListReference


class TunableMixerListInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'mixer_list': TunableAffordanceListReference(),
        'mixer_lists': TunableList(
            description="Additional mixer lists to inject to",
            tunable=TunableAffordanceListReference(pack_safe=True)
        ),
        'mixers': TunableList(
            description="The mixers to inject to the lists",
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        )
    }

    __slots__ = ('mixer_list', 'mixer_lists', 'mixers',)

    def _get_affordance_lists_gen(self):
        if self.mixer_list is not None:
            yield self.mixer_list
        yield from self.mixer_lists

    def inject(self):
        mixers_to_add = set()
        for mixer in self.mixers:
            # Check if subclass instead of using strict class_restrictions in TunableReference
            # to allow modded subclasses
            if mixer is not None:
                if not issubclass(mixer, MixerInteraction):
                    logger.warn("Class does not extend MixerInteraction: {}, skipping in mixer list injection to {}".format(mixer, self.mixer_list))
                    continue
                mixers_to_add.add(mixer)

        for mixer_list in self._get_affordance_lists_gen():
            inject_list(mixer_list, 'value', mixers_to_add)
