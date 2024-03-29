import sims4
from interactions.base.picker_interaction import DefinitionsFromTags, DefinitionsExplicit, InventoryItems, DefinitionsRandom, DefinitionsTested, LimitedItemList, PurchaseToInventory, MailmanDelivery, SlotToParent, DeliveryServiceNPC
from lot51_core import logger
from lot51_core.tunables.multiplier_injection import TunableMultiplierInjection
from lot51_core.utils.collections import AttributeDict
from lot51_core.utils.injection import merge_list, inject_list
from lot51_core.utils.tunables import clone_factory_wrapper_with_overrides
from services import get_instance_manager
from sims4.localization import TunableLocalizedString
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableVariant, TunableReference, TunableTuple, TunableEnumEntry, TunableResourceKey, OptionalTunable, Tunable
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
        'delivery_method_override': TunableVariant(
            description='Where the objects purchased will be delivered.',
            purchase_to_inventory=PurchaseToInventory(description="Purchase the objects directly into a participant's inventory."),
            mailman_delivery=MailmanDelivery(description='Deliver the objects by the mailman.'),
            slot_to_parent=SlotToParent(description=' Deliver the objects by slotting them to a parent object.'),
            delivery_service_npc=DeliveryServiceNPC(description='Purchased objects will be delivered by the delivery service npc.'),
            locked_args={'none': None},
            default='none',
        ),
        'loots_on_purchase': TunableList(
            description='A list of loots to run immediately on each of the items purchased.',
            tunable=TunableReference(
                description='A loot to apply to a purchase.',
                manager=get_instance_manager(Types.ACTION),
                pack_safe=True
            ),
        ),
        'price_multiplier': OptionalTunable(
            tunable=TunableMultiplierInjection.TunableFactory(),
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

    __slots__ = ('additional_picker_categories', 'delivery_method_override', 'price_multiplier', 'purchase_list_option', 'loots_on_purchase', 'use_dropdown_filter_override')

    def _handle_dialog_overrides(self, affordance):
        overrides = AttributeDict()

        if self.use_dropdown_filter_override is not None:
            overrides.use_dropdown_filter = self.use_dropdown_filter_override

        if len(self.additional_picker_categories):
            overrides.categories = merge_list(affordance.picker_dialog.categories, self.additional_picker_categories)

        if len(overrides):
            cloned_dialog = clone_factory_wrapper_with_overrides(affordance.picker_dialog, **overrides)
            setattr(affordance, 'picker_dialog', cloned_dialog)

    def inject_to_affordance(self, affordance):
        if affordance is None:
            logger.error("Failed to inject to purchase picker interaction, affordance not found")
            return

        if hasattr(affordance, 'delivery_method') and self.delivery_method_override is not None:
            affordance.delivery_method_override = self.delivery_method_override

        if hasattr(affordance, 'loots_on_purchase'):
            inject_list(affordance, 'loots_on_purchase', self.loots_on_purchase)

        if hasattr(affordance, 'purchase_list_option'):
            inject_list(affordance, 'purchase_list_option', self.purchase_list_option)

        if hasattr(affordance, 'price_multiplier') and self.price_multiplier is not None:
            self.price_multiplier.inject(affordance, 'price_multiplier')

        if hasattr(affordance, 'picker_dialog'):
            self._handle_dialog_overrides(affordance)
