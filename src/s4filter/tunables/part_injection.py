import services
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list, merge_affordance_filter, inject_dict
from postures.posture import TunablePostureTypeListSnippet
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, OptionalTunable
from snippets import TunableAffordanceFilterSnippet


class TunableObjectPartInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'object_parts': TunableList(
            description="A list of object parts this filter should be injected to",
            tunable=TunableReference(manager=services.get_instance_manager(Types.OBJECT_PART), pack_safe=True),
        ),
        'compatibility': OptionalTunable(
            tunable=TunableAffordanceFilterSnippet(
                description="Affordance filter to merge with object part supported_affordance_data"
            ),
        ),
        'supported_posture_types': OptionalTunable(
            tunable=TunablePostureTypeListSnippet(
                description='The postures supported by this part. If empty, assumes all postures are supported.'
            ),
        ),
    }

    __slots__ = ('object_parts', 'compatibility', 'supported_posture_types',)

    def inject(self):
        for part in self.object_parts:
            try:
                if self.compatibility is not None and hasattr(part, 'supported_affordance_data'):
                    # merge the current row's compatibility filter into each object part
                    compatibility = merge_affordance_filter(
                        part.supported_affordance_data.compatibility,
                        other_filter=self.compatibility,
                    )
                    inject_dict(part, 'supported_affordance_data', compatibility=compatibility)
            except:
                logger.exception("failed compatibility injection to object part: {}".format(part))

            try:
                if self.supported_posture_types is not None and hasattr(part, 'supported_posture_types'):
                    inject_list(part, 'supported_posture_types', self.supported_posture_types)
            except:
                logger.exception("failed supported posture types injection to object part: {}".format(part))