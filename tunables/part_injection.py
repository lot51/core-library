import services
from lot51_core import logger
from postures.posture import TunablePostureTypeListSnippet
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableReference, TunableList, OptionalTunable
from snippets import TunableAffordanceFilterSnippet


class TunableObjectPartInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'object_parts': TunableList(
            description="A list of object parts this filter should be injected to",
            tunable=TunableReference(manager=services.get_instance_manager(Types.OBJECT_PART))
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
            # skip obj parts that failed to load
            if part is None or not hasattr(part, 'supported_affordance_data'):
                continue

            try:
                if self.compatibility is not None:
                    # merge the current row's compatibility filter into each object part
                    compat = part.supported_affordance_data.compatibility
                    new_included_list = self.compatibility._tuned_values.default_inclusion.include_affordances + compat._tuned_values.default_inclusion.include_affordances
                    new_excluded_list = self.compatibility._tuned_values.default_inclusion.exclude_affordances + compat._tuned_values.default_inclusion.exclude_affordances

                    new_default_inclusion = compat._tuned_values.default_inclusion.clone_with_overrides(include_affordances=new_included_list, exclude_affordances=new_excluded_list)
                    compat._tuned_values = compat._tuned_values.clone_with_overrides(default_inclusion=new_default_inclusion)
            except:
                logger.exception("failed compatibility injection to object part: {}".format(part))

            try:
                if self.supported_posture_types is not None:
                    part.supported_posture_types += self.supported_posture_types
            except:
                logger.exception("failed supported posture types injection to object part: {}".format(part))