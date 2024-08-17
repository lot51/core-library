from event_testing.tests import TunableTestSet
from interactions.utils.success_chance import SuccessChance
from lot51_core.loot import LotFiftyOneCoreLootActionVariant
from lot51_core.tunables.delivery_method import FglDeliveryMethod, InventoryDeliveryMethod, \
    MultipleInventoriesDeliveryMethod, MailboxDeliveryMethod, HouseholdInventoryDeliveryMethod
from lot51_core.tunables.definition_query import DefinitionSearchMethodVariant
from services import get_instance_manager
from sims4.localization import TunableLocalizedStringFactory
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableVariant, TunableTuple, TunableList, Tunable, OptionalTunable, TunableInterval, TunableEnumSet, TunableReference
from tag import Tag
from tunable_multiplier import TunableMultiplier


class TunablePurchaseItemSource(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'definition_source': DefinitionSearchMethodVariant(),
        'kit_item_sources': TunableList(
            description="A list of potential objects that will be spawned in `definition_source` inventory on purchase (The final object's tuning must have an inventory component to suppor this feature).",
            tunable=TunableTuple(
                definition_source=DefinitionSearchMethodVariant(),
                quantity=TunableInterval(tunable_type=int, default_lower=1, default_upper=1),
                chance=SuccessChance.TunableFactory(),
            )
        )
    }

    def get_definition_data_gen(self, *args, **kwargs):
        yield from self.definition_source.get_definition_data_gen(*args, **kwargs)


class TunablePurchaseItem(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'stock_id': Tunable(description="Unique Stock ID override, by default will set a UUID", tunable_type=str, default=None, allow_empty=True),
        'actions_on_creation': TunableList(
            description="Loot to reward to each object purchased.",
            tunable=LotFiftyOneCoreLootActionVariant(),
        ),
        'category_tags': TunableEnumSet(enum_type=Tag, invalid_enums=(Tag.INVALID,)),
        'chance': SuccessChance.TunableFactory(description="Chance for each item source selection to be included"),
        'custom_price': OptionalTunable(
            description="Overrides the default catalog price",
            tunable=Tunable(tunable_type=int, default=0)
        ),
        'custom_names': OptionalTunable(
            description="A random name will be selected and set as the custom name of the object, use the `set_custom_name_on_object` tunable below to toggle whether it is actually set in the name component.",
            tunable=TunableList(
                tunable=Tunable(tunable_type=str, default=None, allow_empty=True),
            )
        ),
        'delivery_override': TunableVariant(
            description="Where to spawn objects on successful purchase.",
            participant_fgl=FglDeliveryMethod.TunableFactory(),
            inventory=InventoryDeliveryMethod.TunableFactory(),
            household_inventory=HouseholdInventoryDeliveryMethod.TunableFactory(),
            mailbox=MailboxDeliveryMethod.TunableFactory(),
            multiple_inventories=MultipleInventoriesDeliveryMethod.TunableFactory(),
        ),
        'display_name_override': OptionalTunable(
            description="Override the display name of the object in the picker. (Does not override custom_names)",
            tunable=TunableLocalizedStringFactory()
        ),
        'description_override': OptionalTunable(
            description="Override the object catalog description",
            tunable=TunableLocalizedStringFactory()
        ),
        'disabled_description': OptionalTunable(
            description="Description to display if row is disabled",
            tunable=TunableLocalizedStringFactory()
        ),
        'enable_tests': TunableTestSet(description="Tests to decide if row is not greyed out (not cached)"),
        'exclude_from_stock_management': Tunable(tunable_type=bool, default=False),
        'hide_if_sold_out': Tunable(description="Hides from picker if stock level is 0 instead of showing sold out text/icon", tunable_type=bool, default=False),
        'include_build_buy_tags': Tunable(description="Toggle the objects catalog tags to be included in the category tags", tunable_type=bool, default=False),
        'include_recipe_tags': Tunable(description="Toggle the recipe tags to be included in the category tags", tunable_type=bool, default=False),
        'item_sources': TunableList(
            description="Definitions and Recipes to include in picker. Each source generates an additional row in the picker.",
            tunable=DefinitionSearchMethodVariant()
            # tunable=TunablePurchaseItemSource.TunableFactory()
        ),
        'limited_stock': OptionalTunable(
            tunable=TunableInterval(tunable_type=int, default_lower=1, default_upper=1, minimum=0)
        ),
        'price_multiplier': TunableMultiplier.TunableFactory(description="A multiplier only applied to this purchase item's price  (not cached)"),
        'depreciation_multiplier': TunableMultiplier.TunableFactory(description="A multiplier applied to the object value upon purchase (not cached)"),
        'quality_states': TunableList(
            description="An item from this list will be randomly selected to add additional value/quality to an object",
            tunable=TunableTuple(
                states=TunableList(tunable=TunableReference(manager=get_instance_manager(Types.OBJECT_STATE))),
                static_price_multiplier=Tunable(tunable_type=float, default=1),
                static_depreciation_multiplier=Tunable(tunable_type=float, default=1),
                weight=TunableMultiplier.TunableFactory(),
            )
        ),
        'set_custom_name_on_object': Tunable(description="If custom_names is enabled, the chosen name will be set in the NAME_COMPONENT and provided as the 0 index token in description. Set to false to only use the custom name for the description.", tunable_type=bool, default=True),
        'set_sim_as_owner': Tunable(tunable_type=bool, default=False),
        'show_discount': Tunable(tunable_type=bool, default=False),
        'use_base_cost_as_value': Tunable(tunable_type=bool, default=False, description="Instead of using the purchase price, the original base cost will be set as the purchased object's value."),
        'visibility_tests': TunableTestSet(description="Tests to decide if row is visible (not cached)"),
    }
