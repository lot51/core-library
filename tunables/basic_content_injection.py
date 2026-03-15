from interactions.base.basic import FlexibleLengthContent, _StagingContentBase
from interactions.utils.tunable import TunableAffordanceLinkList
from interactions.utils.statistic_element import TunableExitConditionSnippet, PeriodicStatisticChangeElement
from lot51_core import logger
from lot51_core.utils.collections import AttributeDict
from lot51_core.utils.injection import merge_dict, merge_list
from lot51_core.utils.tunables import clone_factory_wrapper_with_overrides, clone_factory_with_overrides
from sims4.tuning.tunable import TunableList, OptionalTunable, HasTunableSingletonFactory, AutoFactoryInit, Tunable, \
    TunableTuple
from snippets import TunableAffordanceListReference


class TunableBasicContentInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'conditional_actions': TunableList(
            description="Only used for interactions with a flexible_length basic_content.",
            tunable=TunableExitConditionSnippet(
                pack_safe=True
            )
        ),
        'periodic_stat_change': OptionalTunable(
            description="Only used for interactions with a flexible_length basic_content.",
            tunable=PeriodicStatisticChangeElement.TunableFactory(
                locked_args={'show_while_routing': False}
            )
        ),
        'staging_content': OptionalTunable(
            description="Only used for interactions with a flexible_length basic_content and staging_content content.",
            tunable=TunableTuple(
                affordance_links=TunableAffordanceLinkList(class_restrictions=('MixerInteraction',)),
                affordance_lists=TunableList(TunableAffordanceListReference(pack_safe=True)),
            )
        ),
        'start_autonomous_inertial_override': OptionalTunable(
            description="Only used for interactions with a flexible_length basic_content.",
            tunable=Tunable(tunable_type=bool, default=True),
        ),
        'start_user_directed_inertial_override': OptionalTunable(
            description="Only used for interactions with a flexible_length basic_content.",
            tunable=Tunable(tunable_type=bool, default=True),
        ),
    }

    __slots__ = ('periodic_stat_change', 'conditional_actions', 'staging_content', 'start_autonomous_inertial_override', 'start_user_directed_inertial_override')

    def inject_to_affordance(self, affordance):
        overrides = AttributeDict()

        # Periodic Stat Change
        if self.periodic_stat_change is not None:
            if isinstance(affordance.basic_content, FlexibleLengthContent):
                periodic_stat_change = affordance.basic_content.periodic_stat_change
                if periodic_stat_change is not None:
                    overrides.periodic_stat_change = clone_factory_wrapper_with_overrides(
                        periodic_stat_change,
                        operation_actions=merge_dict(periodic_stat_change.operation_actions, actions=merge_list(periodic_stat_change.operation_actions.actions, self.periodic_stat_change.operation_actions.actions)),
                        operations=merge_list(periodic_stat_change.operations, self.periodic_stat_change.operations)
                    )
                else:
                    logger.warn('Cannot inject periodic_stat_change to {}. This affordance does not have existing periodic_stat_change content.'.format(affordance))
            else:
                logger.warn('Cannot inject periodic_stat_change to {}. This affordance does not use flexible_content basic_content.'.format(affordance))

        # Conditional Actions
        if len(self.conditional_actions):
            if isinstance(affordance.basic_content, FlexibleLengthContent):
                overrides.conditional_actions = merge_list(affordance.basic_content.conditional_actions, self.conditional_actions)
            else:
                logger.warn('Cannot inject conditional_actions to {}. This affordance does not use flexible_content basic_content.'.format(affordance))

        if self.staging_content is not None:
            if isinstance(affordance.basic_content, FlexibleLengthContent):
                content = affordance.basic_content.content
                if isinstance(content, _StagingContentBase):
                    content_set_overrides = AttributeDict()
                    if self.staging_content.affordance_links:
                        content_set_overrides.affordance_links = merge_list(content.content_set.affordance_links, new_items=self.staging_content.affordance_links)

                    if self.staging_content.affordance_lists:
                        content_set_overrides.affordance_lists = merge_list(content.content_set.affordance_lists, new_items=self.staging_content.affordance_lists)

                    if content_set_overrides:
                        new_content_set = clone_factory_wrapper_with_overrides(content.content_set, **content_set_overrides)
                        overrides.content = clone_factory_with_overrides(content, content_set=new_content_set)
                        # Rerun _tunable_loaded_callback
                        affordance._content_sets_cls = new_content_set()
                else:
                    logger.warn("Cannot inject staging content to {}. This affordance does not use staging_content content.".format(affordance))
            else:
                logger.warn("Cannot inject staging content to {}. This affordance does not use flexible_content basic_content.".format(affordance))

        if self.start_autonomous_inertial_override is not None:
            if isinstance(affordance.basic_content, FlexibleLengthContent):
                overrides.start_autonomous_inertial = self.start_autonomous_inertial_override
            else:
                logger.warn('Cannot inject start_autonomous_inertial to {}. This affordance does not use flexible_content basic_content.'.format(affordance))

        if self.start_user_directed_inertial_override is not None:
            if isinstance(affordance.basic_content, FlexibleLengthContent):
                overrides.start_user_directed_inertial = self.start_user_directed_inertial_override
            else:
                logger.warn('Cannot inject start_user_directed_inertial to {}. This affordance does not use flexible_content basic_content.'.format(affordance))

        # Apply overrides
        if len(overrides):
            # logger.info("Basic Content Overrides: {} <- {}".format(affordance, overrides))
            affordance.basic_content = clone_factory_with_overrides(affordance.basic_content, **overrides)
