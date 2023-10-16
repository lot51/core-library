from interactions.utils.tunable_icon import TunableIcon, TunableIconFactory
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, OptionalTunable


class TunableDisplayData(HasTunableSingletonFactory, AutoFactoryInit):

    FACTORY_TUNABLES = {
        'instance_display_name': OptionalTunable(tunable=TunableLocalizedStringFactory()),
        'instance_display_description': OptionalTunable(tunable=TunableLocalizedStringFactory()),
        'instance_display_icon': OptionalTunable(tunable=TunableIconFactory()),
    }

    def get_name(self, *tokens):
        if self.instance_display_name is not None:
            return self.instance_display_name(*tokens)

    def get_description(self, *tokens):
        if self.instance_display_description is not None:
            return self.instance_display_description(*tokens)

    def get_icon(self, resolver=None):
        if self.instance_display_icon is not None:
            return self.instance_display_icon(resolver)