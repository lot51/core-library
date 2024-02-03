import sims4
from interactions.base.picker_interaction import DefinitionsFromTags, DefinitionsExplicit, InventoryItems, DefinitionsRandom, DefinitionsTested, LimitedItemList
from lot51_core import logger
from lot51_core.utils.collections import AttributeDict
from services import get_instance_manager
from sims4.localization import TunableLocalizedString
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableVariant, \
    TunableReference, TunableTuple, TunableEnumEntry, TunableResourceKey, OptionalTunable, Tunable
from tag import Tag


class TunablePurchaseInteractionInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'additional_picker_categories': TunableList(
            description='A list of categories that will be displayed in the picker.',
            tunable=TunableTuple(
                description='Tuning for a single category in the picker.',
                tag=TunableEnumEntry(
                    description='A single tag used for filtering items.  If an item in the picker has this tag then it will be displayed in this category.',
                    tunable_type=Tag,
                    default=Tag.INVALID
                ),
                icon=TunableResourceKey(
                    description='Icon that represents this category.',
                    default=None,
                    resource_types=sims4.resources.CompoundTypes.IMAGE
                ),
                tooltip=TunableLocalizedString(
                    description='A localized string for the tooltip of the category.'
                ),
                disabled_tooltip=OptionalTunable(
                    description='If enabled then when there are no items in this category, the button will be disabled instead of hidden and will have this tooltip explaining why it is hidden.',
                    tunable=TunableLocalizedString(
                        description='The string to display as a tooltip when the category button is disabled because it is empty.'
                    )
                )
            ),
        ),
        'loots_on_purchase': TunableList(
            description='A list of loots to run immediately on each of the items purchased.',
            tunable=TunableReference(
                description='A loot to apply to a purchase.',
                manager=get_instance_manager(Types.ACTION),
                pack_safe=True
            ),
        ),
        'purchase_list_option': TunableList(
            description='A list of methods that will be used to generate the list of objects that are available in the picker.',
            tunable=TunableVariant(
                description='The method that will be used to generate the list of objects that will populate the picker.',
                all_items=DefinitionsFromTags.TunableFactory(
                    description='Look through all the items that are possible to purchase. This should be accompanied with specific filtering tags in Object Populate Filter to get a good result.'
                ),
                specific_items=DefinitionsExplicit.TunableFactory(
                    description='A list of specific items that will be purchasable through this dialog.'
                ),
                inventory_items=InventoryItems.TunableFactory(
                    description='Looks at the objects that are in the inventory of the desired participant and returns them based on some criteria.'
                ),
                random_items=DefinitionsRandom.TunableFactory(
                    description='Randomly selects items based on a weighted list.'
                ),
                tested_items=DefinitionsTested.TunableFactory(
                    description='Test items that are able to be displayed within the picker.'
                ),
                limited_items=LimitedItemList.TunableFactory(
                    description='Items provided by the Purchase Picker Service.'
                ),
                default='all_items'
            ),
        ),
        'use_dropdown_filter_override': OptionalTunable(
            tunable=Tunable(
                tunable_type=bool,
                default=False
            )
        ),
    }

    __slots__ = ('additional_picker_categories', 'purchase_list_option', 'loots_on_purchase', 'use_dropdown_filter_override')

    def inject_to_affordance(self, affordance):
        if affordance is None:
            logger.error("Failed to inject to purchase picker interaction, affordance not found")
            return

        if getattr(affordance, 'purchase_list_option', None) is not None:
            affordance.purchase_list_option += self.purchase_list_option

        if getattr(affordance, 'loots_on_purchase', None) is not None:
            affordance.loots_on_purchase += self.loots_on_purchase

        if getattr(affordance, 'picker_dialog', None) is not None:
            overrides = AttributeDict()
            overrides.categories = affordance.picker_dialog._tuned_values.categories + self.additional_picker_categories

            if self.use_dropdown_filter_override is not None:
                overrides.use_dropdown_filter = self.use_dropdown_filter_override

            affordance.picker_dialog._tuned_values = affordance.picker_dialog._tuned_values.clone_with_overrides(**overrides)
