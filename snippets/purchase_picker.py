import math
import random
import build_buy
import enum
import services
import sims4.random
import uuid
from crafting.crafting_interactions import create_craftable
from date_and_time import create_time_span, TimeSpan
from distributor.shared_messages import IconInfoData
from event_testing.resolver import SingleObjectResolver
from event_testing.tests import TunableTestSet
from interactions.payment.payment_source import get_tunable_payment_source_variant
from interactions.picker.object_marketplace_picker_interaction import ObjectMarketplacePickerInteraction
from interactions.utils.success_chance import SuccessChance
from interactions.utils.tunable_icon import TunableIcon
from lot51_core import logger
from interactions import ParticipantType
from lot51_core.loot import LotFiftyOneCoreLootActionVariant
from lot51_core.tunables.definition_query import DefinitionSearchMethodVariant
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from lot51_core.utils.math import chance_succeeded
from lot51_core.utils.placement import get_location_near_location, get_location_near_object
from objects.components.name_component import NameComponent
from objects.components.state import ObjectStateValue
from objects.components.types import NAME_COMPONENT
from objects.system import create_object
from objects.terrain import TerrainPoint
from sims.sim_info import SimInfo
from sims4.localization import TunableLocalizedStringFactory, _create_localized_string, LocalizationHelperTuning
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableVariant, TunableTuple, TunableList, TunableReference, Tunable, OptionalTunable, TunableInterval, TunableEnumSet, TunableSimMinute, HasTunableReference
from tag import Tag
from tunable_multiplier import TunableMultiplier
from ui.ui_dialog_notification import UiDialogNotification
from ui.ui_dialog_picker import PurchasePickerRow, UiPurchasePicker


class FglDeliveryMethod(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'participant_type': TunableEnumEntry(tunable_type=ParticipantType, default=ParticipantType.Object),
        'optimal_distance': Tunable(tunable_type=float, default=0),
        'radius_width': Tunable(tunable_type=float, default=8),
        'max_distance': Tunable(tunable_type=float, default=8),
        'x_random_offset': OptionalTunable(tunable=TunableInterval(tunable_type=float, default_lower=0, default_upper=0)),
        'z_random_offset': OptionalTunable(tunable=TunableInterval(tunable_type=float, default_lower=0, default_upper=0)),
    }

    __slots__ = ('participant_type', 'optimal_distance', 'radius_width', 'max_distance', 'x_random_offset', 'z_random_offset')

    def __call__(self, resolver, obj):
        participant = resolver.get_participant(self.participant_type)
        if isinstance(participant, TerrainPoint):
            translation, orientation, routing_surface = get_location_near_location(obj, participant.location, optimal_distance=self.optimal_distance, radius_width=self.radius_width, max_distance=self.max_distance, x_range=self.x_random_offset, z_range=self.z_random_offset)
        elif isinstance(participant, SimInfo):
            sim = participant.get_sim_instance()
            translation, orientation, routing_surface = get_location_near_object(obj, sim, optimal_distance=self.optimal_distance, radius_width=self.radius_width, max_distance=self.max_distance, x_range=self.x_random_offset, z_range=self.z_random_offset)
        else:
            translation, orientation, routing_surface = get_location_near_object(obj, participant, optimal_distance=self.optimal_distance, radius_width=self.radius_width, max_distance=self.max_distance, x_range=self.x_random_offset, z_range=self.z_random_offset)

        obj.opacity = 0
        obj.move_to(translation=translation, orientation=orientation, routing_surface=routing_surface)
        obj.fade_in()
        logger.debug("delivering obj to participant {} {}".format(obj, participant))
        return True


class InventoryDeliveryMethod(HasTunableSingletonFactory, AutoFactoryInit):

    class InventoryDeliveryFallback(enum.Int):
        NONE = 0
        ACTIVE_HOUSEHOLD = 1
        ZONE_HOUSEHOLD = 2

    FACTORY_TUNABLES = {
        'inventory_source': ObjectSearchMethodVariant(),
        'fallback_inventory': TunableEnumEntry(tunable_type=InventoryDeliveryFallback, default=InventoryDeliveryFallback.NONE),
    }

    __slots__ = ('inventory_source', 'fallback_inventory',)

    def attempt_fallback_delivery(self, resolver, obj):
        if self.fallback_inventory == InventoryDeliveryMethod.InventoryDeliveryFallback.ACTIVE_HOUSEHOLD:
            active_household_id = services.active_household_id()
            if build_buy.is_household_inventory_available(active_household_id):
                if build_buy.move_object_to_household_inventory(obj):
                    return True
        elif self.fallback_inventory == InventoryDeliveryMethod.InventoryDeliveryFallback.ZONE_HOUSEHOLD:
            current_zone = services.current_zone()
            zone_household = current_zone.get_active_lot_owner_household()
            if zone_household and build_buy.is_household_inventory_available(zone_household.id):
                if build_buy.move_object_to_household_inventory(obj):
                    return True
        return False

    def __call__(self, resolver, obj):
        # attempt to find a valid inventory
        for inventory_owner in self.inventory_source.get_objects_gen(resolver=resolver):
            if inventory_owner.is_sim:
                inventory_owner = inventory_owner.get_sim_instance()
            if inventory_owner.inventory_component is not None:
                if inventory_owner.inventory_component.player_try_add_object(obj):
                    return True
        # otherwise attempt to use fallback inventory
        if self.attempt_fallback_delivery(resolver, obj):
            return True
        # delivery failed
        return False


class PurchaseException(BaseException):
    pass


class PurchaseRowData:
    def __init__(self, *args, **kwargs):
        self.category_tags = set()
        self.custom_name = None
        self.definition_data = None
        self.discount_data = (False, None)
        self.base_cost = 0
        self.purchase_item = None
        self.quality = None
        self.stock_key = None


class StockManager:
    STOCK_LEVEL_ZERO = 0
    STOCK_LEVEL_UNLIMITED = -1
    STOCK_MANAGERS = {}

    @classmethod
    def get_stock_manager(cls, key, refresh_period=None):
        logger.debug("getting stock manager: {}".format(key))
        if key in cls.STOCK_MANAGERS:
            return cls.STOCK_MANAGERS[key]
        stock_manager = cls(refresh_period=refresh_period)
        cls.STOCK_MANAGERS[key] = stock_manager
        return stock_manager

    def __init__(self, refresh_period=1440):
        self._refresh_required = True
        self.refresh_period = refresh_period
        self.stock_map = {}
        self.picker_cache = list()
        self.next_refresh_time = -1

    def get_time_to_refresh(self):
        now = services.time_service().sim_now
        difference = self.next_refresh_time - now.absolute_ticks()
        return TimeSpan(difference)

    def has_picker_cache(self):
        return len(self.picker_cache)

    def add_to_picker_cache(self, purchase_data):
        self.picker_cache.append(purchase_data)

    def get_picker_cache_gen(self):
        if self.has_picker_cache():
            yield from self.picker_cache

    def subtract_stock(self, definition, amount=1):
        if self.is_tracked(definition):
            self.stock_map[definition] = max(0, self.stock_map[definition] - amount)

    def set_stock(self, definition, amount):
        self.stock_map[definition] = amount

    def get_stock(self, definition):
        if self.is_tracked(definition):
            return self.stock_map[definition]
        return -1

    def is_tracked(self, definition):
        return definition in self.stock_map

    def should_refresh(self):
        if self._refresh_required:
            return True
        now = services.time_service().sim_now
        if now.absolute_ticks() >= self.next_refresh_time:
            self._refresh_required = True
            return True
        return False

    def pre_refresh(self):
        self.stock_map.clear()
        self.picker_cache.clear()
        self.next_refresh_time = self._get_next_refresh_ticks()

    def post_refresh(self):
        self._refresh_required = False

    def _get_next_refresh_ticks(self):
        now = services.time_service().sim_now
        next_time = now + create_time_span(minutes=self.refresh_period)
        return next_time.absolute_ticks()


class TunableStockManagement(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'sold_out_icon': OptionalTunable(tunable=TunableIcon()),
        'sold_out_description': OptionalTunable(tunable=TunableLocalizedStringFactory()),
        'refresh_period': TunableSimMinute(default=1440),
        'show_refresh_time': Tunable(tunable_type=bool, default=True)
    }


class PurchasePickerSnippet(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):

    INSTANCE_TUNABLES = {
        'delivery_method': TunableVariant(
            description="Where to spawn objects on successful purchase.",
            participant_fgl=FglDeliveryMethod.TunableFactory(),
            inventory=InventoryDeliveryMethod.TunableFactory(),
            default='participant_fgl'
        ),
        'loot_on_success': TunableList(
            description="Loot applied to the Actor if at least one item was purchased successfully",
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION))
        ),
        'loot_on_failure': TunableList(
            description="Loot applied to the Actor if at least one item failed to purchase",
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION))
        ),
        'payment_source': get_tunable_payment_source_variant(description="All purchases will be debited from this source"),
        'picker_dialog': UiPurchasePicker.TunableFactory(),
        'price_multiplier': TunableMultiplier.TunableFactory(description="A multiplier applied to all purchase items"),
        'purchase_items': TunableList(
            tunable=TunableTuple(
                stock_id=Tunable(description="Unique Stock ID override, by default will set a UUID", tunable_type=str, default=None, allow_empty=True),
                actions_on_creation=TunableList(
                    tunable=LotFiftyOneCoreLootActionVariant(),
                ),
                category_tags=TunableEnumSet(enum_type=Tag, invalid_enums=(Tag.INVALID,)),
                chance=SuccessChance.TunableFactory(description="Chance for each item source selection to be included"),
                custom_price=OptionalTunable(description="Overrides the default catalog price", tunable=Tunable(tunable_type=int, default=0)),
                custom_names=OptionalTunable(
                    description="A random name will be selected and set as the custom name of the object, use the `set_custom_name_on_object` tunable below to toggle whether it is actually set in the name component.",
                    tunable=TunableList(
                        tunable=Tunable(tunable_type=str, default=None, allow_empty=True),
                    )
                ),
                delivery_override=TunableVariant(
                    description="Where to spawn objects on successful purchase.",
                    participant_fgl=FglDeliveryMethod.TunableFactory(),
                    inventory=InventoryDeliveryMethod.TunableFactory(),
                ),
                description_override=OptionalTunable(description="Override the object catalog description", tunable=TunableLocalizedStringFactory()),
                disabled_description=OptionalTunable(description="Description to display if row is disabled", tunable=TunableLocalizedStringFactory()),
                enable_tests=TunableTestSet(description="Tests to decide if row is not greyed out (not cached)"),
                exclude_from_stock_management=Tunable(tunable_type=bool, default=False),
                hide_if_sold_out=Tunable(description="Hides from picker if stock level is 0 instead of showing sold out text/icon", tunable_type=bool, default=False),
                include_build_buy_tags=Tunable(description="Toggle the objects catalog tags to be included in the category tags", tunable_type=bool, default=False),
                include_recipe_tags=Tunable(description="Toggle the recipe tags to be included in the category tags", tunable_type=bool, default=False),
                item_sources=TunableList(description="Definitions and Recipes to include in picker. Each source generates an additional row in the picker.", tunable=DefinitionSearchMethodVariant()),
                limited_stock=OptionalTunable(tunable=TunableInterval(tunable_type=int, default_lower=1, default_upper=1, minimum=0)),
                price_multiplier=TunableMultiplier.TunableFactory(description="A multiplier only applied to this purchase item's price  (not cached)"),
                quality_states=TunableList(
                    description="An item from this list will be randomly selected to add additional value/quality to an object",
                    tunable=TunableTuple(
                        states=TunableList(tunable=ObjectStateValue.TunableReference()),
                        static_price_multiplier=Tunable(tunable_type=int, default=1),
                        weight=TunableMultiplier.TunableFactory(),
                    )
                ),
                set_custom_name_on_object=Tunable(description="If custom_names is enabled, the chosen name will be set in the NAME_COMPONENT and provided as the 0 index token in description. Set to false to only use the custom name for the description.", tunable_type=bool, default=True),
                set_sim_as_owner=Tunable(tunable_type=bool, default=False),
                show_discount=Tunable(tunable_type=bool, default=False),
                visibility_tests=TunableTestSet(description="Tests to decide if row is visible (not cached)"),
            )
        ),
        'purchase_success_notification': OptionalTunable(tunable=UiDialogNotification.TunableFactory(description="Notification to display if at least one purchase was successful")),
        'purchase_failed_notification': OptionalTunable(tunable=UiDialogNotification.TunableFactory(description="Notification to display if at least one purchase failed")),
        'stock_management': OptionalTunable(tunable=TunableStockManagement.TunableFactory()),
        'show_descriptions': Tunable(tunable_type=bool, default=True),
        'show_tooltips': Tunable(tunable_type=bool, default=True),
        'stop_on_first_failure': Tunable(description="Stop all purchases if an individual item failed to deliver, or had insufficient funds. Otherwise each item will attempt delivery and debit from sim.", tunable_type=bool, default=False),
    }

    __slots__ = ('delivery_method', 'loot_on_success', 'loot_on_failure', 'payment_source', 'picker_dialog', 'price_multiplier', 'purchase_items', 'purchase_success_notification', 'purchase_failed_notification', 'stock_management', 'show_descriptions', 'show_tooltips', 'stop_on_first_failure',)

    @classmethod
    def _tuning_loaded_callback(cls):
        purchase_items = list(cls.purchase_items)
        for ix, row in enumerate(purchase_items):
            if row.stock_id is None:
                purchase_items[ix] = row.clone_with_overrides(stock_id=str(uuid.uuid4()))
        cls.purchase_items = tuple(purchase_items)

    def __init__(self, resolver, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolver = resolver
        self.sim_info = resolver.get_participant(ParticipantType.Actor)
        self.current_item_data = {}
        self.current_price_data = {}
        self._populated_objects = list()

    def get_resolver(self):
        return self.resolver

    def show_picker_dialog(self):
        dialog = self.picker_dialog(self.sim_info, resolver=self.get_resolver())
        dialog.is_sortable = False
        # True returns temp obj ids instead of definition ids
        dialog.purchase_by_object_ids = True
        # True allows the use of `dialog.get_result_definitions_and_counts()`
        dialog.use_dialog_pick_response = True
        dialog.show_description = self.show_descriptions
        dialog.show_description_tooltip = self.show_tooltips

        stock_manager = self.get_stock_manager()
        refreshing = stock_manager and stock_manager.should_refresh()
        # Run pre stock refresh
        if refreshing:
            stock_manager.pre_refresh()

        # Setup "Right Custom Text"
        if self.stock_management is not None:
            if self.stock_management.show_refresh_time:
                refresh_time = stock_manager.get_time_to_refresh()
                dialog.right_custom_text = ObjectMarketplacePickerInteraction.REFRESH_TIME_TEXT(refresh_time)

        for row in self._picker_rows_gen():
            dialog.add_row(row)

        # Run post stock refresh
        if refreshing:
            stock_manager.post_refresh()

        dialog.add_listener(self._on_picker_selected)
        dialog.show_dialog()
        return dialog

    @classmethod
    def get_stock_manager(cls):
        if cls.stock_management is not None:
            return StockManager.get_stock_manager(cls, refresh_period=cls.stock_management.refresh_period)

    def _picker_rows_gen(self):
        resolver = self.get_resolver()

        global_price_multiplier = math.ceil(self.price_multiplier.get_multiplier(resolver))
        stock_manager = self.get_stock_manager()

        # Generate Cached Rows
        if stock_manager and stock_manager.has_picker_cache():
            for picker_data in stock_manager.get_picker_cache_gen():

                definition_data = picker_data.definition_data
                definition = definition_data.definition

                item = picker_data.purchase_item
                quality_info = picker_data.quality
                category_tags = picker_data.category_tags
                base_cost = picker_data.base_cost
                stock_key = picker_data.stock_key

                # Check the global visibility test for this row
                if not item.visibility_tests.run_tests(resolver):
                    continue

                # Recalculate stock if necessary
                current_stock = stock_manager.get_stock(stock_key)
                if item.exclude_from_stock_management and item.limited_stock is not None:
                    current_stock = random.randint(item.limited_stock.lower_bound, item.limited_stock.upper_bound)
                elif current_stock == StockManager.STOCK_LEVEL_UNLIMITED:
                    current_stock = None

                # Skip item if stock has changed and should be hidden
                if item.hide_if_sold_out and current_stock == StockManager.STOCK_LEVEL_ZERO:
                    continue

                # Spawn temporary object
                _post_add = None
                if quality_info:
                    def _post_add(obj):
                        for state_value in quality_info.states:
                            if state_value is not None:
                                obj.set_state(state_value.state, state_value, force_update=True)

                if definition_data.recipe is not None:
                    temp_obj = create_craftable(definition_data.recipe, None, post_add=_post_add)
                else:
                    temp_obj = create_object(definition, post_add=_post_add)

                self._populated_objects.append(temp_obj)

                # Add sim specific multipliers
                cost_multiplier = item.price_multiplier.get_multiplier(resolver)
                price = round(base_cost * cost_multiplier * global_price_multiplier)

                # Check for discount
                is_discounted = item.show_discount and price < base_cost
                prediscounted_price = base_cost if is_discounted else None

                # Test if item should be disabled
                is_enabled = item.enable_tests.run_tests(resolver)

                # Get icon override
                icon_override = None
                # Override the icon with sold out icon
                if self.stock_management.sold_out_icon is not None and current_stock == 0:
                    icon_override = IconInfoData(icon_resource=self.stock_management.sold_out_icon)

                # Get row name override
                if picker_data.custom_name is not None:
                    row_name = LocalizationHelperTuning.get_raw_text(picker_data.custom_name)
                else:
                    row_name = _create_localized_string(build_buy.get_object_catalog_name(definition.id))

                default_description = _create_localized_string(build_buy.get_object_catalog_description(definition.id))
                # Show disabled text override if not available to subject
                if not is_enabled and item.disabled_description is not None:
                    row_description = item.disabled_description(row_name, default_description)
                # Otherwise show out of stock description if stock is managed
                elif self.stock_management and self.stock_management.sold_out_description and current_stock == 0:
                    row_description = self.stock_management.sold_out_description(row_name, default_description)
                # Get row description override
                elif item.description_override is not None:
                    row_description = item.description_override(row_name, default_description)
                # Otherwise fallback to catalog description
                else:
                    row_description = default_description

                # Cache row info for immediate dialog response
                # Assumes dialog.purchase_by_object_ids is set to True.
                self.current_price_data[temp_obj.id] = price
                self.current_item_data[temp_obj.id] = picker_data

                row = PurchasePickerRow(def_id=definition.id, is_enable=is_enabled, objects={temp_obj},
                                        row_description=row_description, num_owned=0, num_available=current_stock,
                                        tags=category_tags, custom_price=price,
                                        icon_info_data_override=icon_override, show_discount=is_discounted,
                                        prediscounted_price=prediscounted_price)
                yield row

            return

        # Otherwise generate new rows
        for item in self.purchase_items:
            # Check the global visibility test for this row
            if not item.visibility_tests.run_tests(resolver):
                continue

            # Generate weighted list of possible quality info for this row
            weighted_qualities = list()
            for row in item.quality_states:
                weight = row.weight.get_multiplier(resolver)
                weighted_qualities.append((weight, row,))

            index = 0

            # Get Definitions from each source
            for item_source in item.item_sources:
                for definition_data in item_source.get_definition_data_gen(resolver=resolver):
                    if definition_data.definition is None:
                        logger.warn("Definition not found")
                        continue

                    # Check the global chance for this row
                    if not chance_succeeded(item.chance.get_chance(resolver)):
                        continue

                    definition = definition_data.definition
                    stock_key = (item.stock_id, definition, index,)

                    # Calculate available stock
                    current_stock = None
                    # Get current stock if managed
                    if stock_manager and not stock_manager.should_refresh() and stock_manager.is_tracked(stock_key) and not item.exclude_from_stock_management:
                        _stock_amount = stock_manager.get_stock(stock_key)
                        if _stock_amount > StockManager.STOCK_LEVEL_UNLIMITED:
                            current_stock = _stock_amount
                    # Otherwise get a random limited stock
                    elif item.limited_stock is not None:
                        current_stock = random.randint(item.limited_stock.lower_bound, item.limited_stock.upper_bound)
                        if stock_manager and not item.exclude_from_stock_management:
                            # Update stock manager for refresh
                            stock_manager.set_stock(stock_key, current_stock)

                    # Skip object if sold out and should hide
                    if item.hide_if_sold_out and current_stock == StockManager.STOCK_LEVEL_ZERO:
                        continue

                    # Select quality states and add to temp object
                    quality_info = None
                    _post_add = None
                    if len(weighted_qualities) > 0:
                        quality_info = sims4.random.weighted_random_item(weighted_qualities)

                        def _post_add(obj):
                            for state_value in quality_info.states:
                                if state_value is not None:
                                    obj.set_state(state_value.state, state_value, force_update=True)

                    if definition_data.recipe is not None:
                        temp_obj = create_craftable(definition_data.recipe, None, post_add=_post_add)
                    else:
                        temp_obj = create_object(definition, post_add=_post_add)

                    self._populated_objects.append(temp_obj)

                    # Get all category tags
                    category_tags = set(item.category_tags)
                    if item.include_build_buy_tags:
                        # Add definition catalog tags
                        category_tags = category_tags.union(definition.build_buy_tags)

                    # Include recipe tags
                    if item.include_recipe_tags and definition_data.recipe is not None:
                        category_tags = category_tags.union(definition_data.recipe.recipe_tags)

                    # Calculate price
                    base_cost = item.custom_price if item.custom_price is not None else definition.price

                    # Add quality_info multiplier
                    if quality_info is not None:
                        base_cost *= quality_info.static_price_multiplier

                    # Add sim specific multipliers
                    cost_multiplier = item.price_multiplier.get_multiplier(resolver)
                    price = round(base_cost * cost_multiplier * global_price_multiplier)

                    # Check for discount
                    is_discounted = item.show_discount and price < base_cost
                    prediscounted_price = base_cost if is_discounted else None

                    # Test if item should be disabled
                    is_enabled = item.enable_tests.run_tests(resolver)

                    # Get icon override
                    icon_override = None
                    # Override the icon with sold out icon
                    if self.stock_management.sold_out_icon is not None and current_stock == StockManager.STOCK_LEVEL_ZERO:
                        icon_override = IconInfoData(icon_resource=self.stock_management.sold_out_icon)

                    # Get Custom Name
                    custom_name = None
                    if item.custom_names is not None:
                        custom_name = random.choice(item.custom_names)

                    # Get row name override
                    if custom_name is not None:
                        row_name = LocalizationHelperTuning.get_raw_text(custom_name)
                    # Otherwise fallback to catalog name
                    else:
                        row_name = _create_localized_string(build_buy.get_object_catalog_name(definition.id))

                    # Show disabled text override if not available to subject
                    default_description = _create_localized_string(build_buy.get_object_catalog_description(definition.id))

                    if not is_enabled and item.disabled_description is not None:
                        row_description = item.disabled_description(row_name, default_description)
                    # Otherwise show out of stock description if stock is managed
                    elif self.stock_management and self.stock_management.sold_out_description and current_stock == StockManager.STOCK_LEVEL_ZERO:
                        row_description = self.stock_management.sold_out_description(row_name, default_description)
                    # Get row description override
                    elif item.description_override is not None:
                        row_description = item.description_override(row_name, default_description)
                    # Otherwise fallback to catalog description
                    else:
                        row_description = default_description

                    # Cache item data
                    picker_data = PurchaseRowData()
                    picker_data.base_cost = base_cost
                    picker_data.category_tags = category_tags
                    picker_data.custom_name = custom_name
                    picker_data.definition = definition
                    picker_data.definition_data = definition_data
                    picker_data.purchase_item = item
                    picker_data.quality = quality_info
                    picker_data.stock_key = stock_key

                    # Cache row info for immediate dialog response
                    # Assumes dialog.purchase_by_object_ids is set to True.
                    self.current_price_data[temp_obj.id] = price
                    self.current_item_data[temp_obj.id] = picker_data

                    # Cache picker row for future use
                    if stock_manager:
                        stock_manager.add_to_picker_cache(picker_data)

                    # Increment row index for stock key
                    index += 1

                    row = PurchasePickerRow(def_id=definition.id, is_enable=is_enabled, objects={temp_obj},
                                            row_description=row_description, num_owned=0,
                                            num_available=current_stock, tags=category_tags,
                                            custom_price=price, icon_info_data_override=icon_override,
                                            show_discount=is_discounted, prediscounted_price=prediscounted_price)
                    yield row

    def _show_purchase_notification(self, dialog_factory, resolver, tokens=()):
        if dialog_factory is not None:
            dialog = dialog_factory(self.sim_info, resolver=resolver)
            dialog.show_dialog(additional_tokens=tokens)

    def _on_picker_selected(self, dialog):
        try:
            if dialog.accepted:
                resolver = dialog._resolver
                obj_ids, counts = dialog.get_result_definitions_and_counts()
                purchase_count = 0
                failed_count = 0
                total_debit = 0

                stock_manager = self.get_stock_manager()

                for obj_id in obj_ids:
                    amount_to_purchase = counts[obj_ids.index(obj_id)]

                    # Aggregate failure count and stop looping if flagged to stop
                    if self.stop_on_first_failure and failed_count > 0:
                        failed_count += amount_to_purchase
                        continue

                    purchase_data = self.current_item_data[obj_id]
                    price = self.current_price_data[obj_id]
                    stock_key = purchase_data.stock_key

                    # Generate each item based on quantity purchased
                    for x in range(amount_to_purchase):
                        try:
                            # Attempt payment
                            if price > 0 and not self.payment_source.try_remove_funds(self.sim_info, price, resolver=resolver):
                                raise PurchaseException("NOT_ENOUGH_FUNDS")

                            # Object Creation
                            if purchase_data.definition_data.recipe is not None:
                                # Attempt to craft object from recipe if available
                                obj = create_craftable(purchase_data.definition_data.recipe, None)
                            else:
                                # Otherwise create object from definition
                                obj = create_object(purchase_data.definition)

                            if obj is None:
                                raise PurchaseException("CREATE_FAILED")

                            # Apply quality states
                            if purchase_data.quality is not None:
                                for state_value in purchase_data.quality.states:
                                    if state_value is not None:
                                        obj.set_state(state_value.state, state_value)

                            # Apply individual loot actions on object creation
                            obj_resolver = SingleObjectResolver(obj)
                            for loot_action in purchase_data.purchase_item.actions_on_creation:
                                loot_action.apply_to_resolver(obj_resolver)

                            # Set Custom Name
                            if purchase_data.custom_name is not None and purchase_data.purchase_item.set_custom_name_on_object:
                                if not obj.has_component(NAME_COMPONENT):
                                    obj.add_component(NameComponent(obj, allow_name=True, allow_description=False))
                                obj.name_component.set_custom_name(purchase_data.custom_name)

                            # Set Ownership
                            obj.set_household_owner_id(self.sim_info.household.id)
                            if purchase_data.purchase_item.set_sim_as_owner and obj.ownable_component:
                                obj.ownable_component.update_sim_ownership(self.sim_info.sim_id)

                            # Set object value to purchase price
                            obj.current_value = price

                            # Attempt to deliver object
                            if purchase_data.purchase_item.delivery_override is not None:
                                delivery_method = purchase_data.purchase_item.delivery_override
                                logger.debug("using delivery override: {}".format(delivery_method))
                            else:
                                delivery_method = self.delivery_method

                            if not delivery_method(resolver, obj):
                                obj.destroy()
                                raise PurchaseException("DELIVERY_FAILED")

                            # Increment debit and purchase count
                            total_debit += price
                            purchase_count += 1

                            # Subtract from stock if managed
                            if stock_manager:
                                stock_manager.subtract_stock(stock_key)

                        except PurchaseException:
                            logger.exception("Delivery failed reason: {}".format(stock_key))
                            # Aggregate failure count and stop looping if flagged to stop
                            if self.stop_on_first_failure:
                                failed_count += amount_to_purchase
                                break
                            # Increment failed count when an individual purchase fails
                            else:
                                failed_count += 1
                                continue

                if purchase_count > 0:
                    for loot in self.loot_on_success:
                        loot.apply_to_resolver(resolver)

                    self._show_purchase_notification(self.purchase_success_notification, resolver, tokens=(purchase_count, failed_count, total_debit,))

                if failed_count > 0:
                    for loot in self.loot_on_failure:
                        loot.apply_to_resolver(resolver)

                    self._show_purchase_notification(self.purchase_failed_notification, resolver, tokens=(purchase_count, failed_count, total_debit,))
        except:
            logger.exception("failed purchasing")
        finally:
            logger.debug("clearing purchase data")
            self.current_item_data.clear()
            self.current_price_data.clear()
            for obj in self._populated_objects:
                obj.destroy()
