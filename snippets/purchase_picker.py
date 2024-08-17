import random
import build_buy
import services
import sims4.random
import uuid
from crafting.crafting_interactions import create_craftable
from date_and_time import create_time_span, TimeSpan
from distributor.shared_messages import IconInfoData
from event_testing.resolver import SingleObjectResolver, SingleActorAndObjectResolver
from interactions.payment.payment_info import PaymentInfo
from interactions.payment.payment_source import get_tunable_payment_source_variant
from interactions.picker.object_marketplace_picker_interaction import ObjectMarketplacePickerInteraction
from interactions.utils.tunable_icon import TunableIcon
from lot51_core import logger
from interactions import ParticipantTypeSingle
from lot51_core.services.events import event_handler, CoreEvent
from lot51_core.snippets.purchase_picker_modifier import PurchasePickerModifier
from lot51_core.tunables.delivery_method import FglDeliveryMethod, MultipleInventoriesDeliveryMethod, \
    InventoryDeliveryMethod, MailboxDeliveryMethod, HouseholdInventoryDeliveryMethod
from lot51_core.tunables.payment_destination import TunablePaymentDestinationVariant
from lot51_core.tunables.purchase_item import TunablePurchaseItem
from lot51_core.utils.collections import AttributeDict
from lot51_core.utils.math import chance_succeeded
from objects.components.name_component import NameComponent
from objects.components.types import NAME_COMPONENT
from objects.system import create_object
from sims4.localization import TunableLocalizedStringFactory, _create_localized_string, LocalizationHelperTuning
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableVariant, TunableList, \
    TunableReference, Tunable, OptionalTunable, TunableSimMinute, HasTunableReference, TunableEnumEntry
from tunable_multiplier import TunableMultiplier
from ui.ui_dialog_notification import UiDialogNotification
from ui.ui_dialog_picker import PurchasePickerRow, UiPurchasePicker


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
        self.purchase_item_source = None
        self.quality = None
        self.stock_key = None
        self.additional_data = AttributeDict()


class StockManager:
    STOCK_LEVEL_ZERO = 0
    STOCK_LEVEL_UNLIMITED = -1
    STOCK_MANAGERS = {}
    DEFAULT_REFRESH_PERIOD = 1440

    @classmethod
    def get_stock_manager(cls, key, refresh_period=DEFAULT_REFRESH_PERIOD):
        if key in cls.STOCK_MANAGERS:
            return cls.STOCK_MANAGERS[key]
        stock_manager = cls(refresh_period=refresh_period)
        cls.STOCK_MANAGERS[key] = stock_manager
        return stock_manager

    @classmethod
    def clear_stock_managers(cls):
        cls.STOCK_MANAGERS.clear()

    def __init__(self, refresh_period=DEFAULT_REFRESH_PERIOD):
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

    def subtract_stock(self, stock_key, amount=1):
        if self.is_tracked(stock_key):
            self.stock_map[stock_key] = max(0, self.stock_map[stock_key] - amount)

    def set_stock(self, stock_key, amount):
        self.stock_map[stock_key] = amount

    def get_stock(self, stock_key):
        if self.is_tracked(stock_key):
            return self.stock_map[stock_key]
        return -1

    def is_tracked(self, stock_key):
        return stock_key in self.stock_map

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
        'refresh_period': TunableSimMinute(default=StockManager.DEFAULT_REFRESH_PERIOD),
        'show_refresh_time': Tunable(tunable_type=bool, default=True)
    }


class PurchasePickerSnippet(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):

    INSTANCE_TUNABLES = {
        'owner_participant': TunableEnumEntry(
            description="The Sim to perform/own purchases. Usually should be Actor.",
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Actor
        ),
        'delivery_method': TunableVariant(
            description="Where to spawn objects on successful purchase.",
            household_inventory=HouseholdInventoryDeliveryMethod.TunableFactory(),
            inventory=InventoryDeliveryMethod.TunableFactory(),
            mailbox=MailboxDeliveryMethod.TunableFactory(),
            multiple_inventories=MultipleInventoriesDeliveryMethod.TunableFactory(),
            participant_fgl=FglDeliveryMethod.TunableFactory(),
            default='participant_fgl'
        ),
        'loot_on_success': TunableList(
            description="Loot applied to the Actor if at least one item was purchased successfully",
            tunable=TunableReference(
                manager=services.get_instance_manager(Types.ACTION),
                pack_safe=True,
            )
        ),
        'loot_on_failure': TunableList(
            description="Loot applied to the Actor if at least one item failed to purchase",
            tunable=TunableReference(
                manager=services.get_instance_manager(Types.ACTION),
                pack_safe=True,
            )
        ),
        'payment_source': get_tunable_payment_source_variant(description="All purchases will be debited from this source"),
        'payment_destination': TunablePaymentDestinationVariant(description="If enabled, the total debited amount will be credited to this destination."),
        'picker_dialog': UiPurchasePicker.TunableFactory(),
        'price_multiplier': TunableMultiplier.TunableFactory(description="A multiplier applied to all purchase items"),
        'purchase_items': TunableList(
            tunable=TunablePurchaseItem.TunableFactory(),
        ),
        'purchase_success_notification': OptionalTunable(
            tunable=UiDialogNotification.TunableFactory(description="Notification to display if at least one purchase was successful")
        ),
        'purchase_failed_notification': OptionalTunable(
            tunable=UiDialogNotification.TunableFactory(description="Notification to display if at least one purchase failed")
        ),
        'stock_management': OptionalTunable(
            tunable=TunableStockManagement.TunableFactory()
        ),
        'show_descriptions': Tunable(tunable_type=bool, default=True),
        'show_tooltips': Tunable(tunable_type=bool, default=True),
        'stop_on_first_failure': Tunable(description="Stop all purchases if an individual item failed to deliver, or had insufficient funds. Otherwise each item will attempt delivery and debit from sim.", tunable_type=bool, default=False),
    }

    __slots__ = ('owner_participant', 'delivery_method', 'loot_on_success', 'loot_on_failure', 'payment_source', 'payment_destination', 'picker_dialog', 'price_multiplier', 'purchase_items', 'purchase_success_notification', 'purchase_failed_notification', 'stock_management', 'show_descriptions', 'show_tooltips', 'stop_on_first_failure',)

    @classmethod
    def _tuning_loaded_callback(cls):
        for row in cls.purchase_items:
            if row.stock_id is None:
                row.stock_id = str(uuid.uuid4())

    def __init__(self, resolver, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolver = resolver
        self.sim_info = resolver.get_participant(self.owner_participant)
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

    def get_purchase_items_gen(self, include_modifiers=True):
        yield from self.purchase_items
        if include_modifiers:
            for snippet in services.get_instance_manager(Types.SNIPPET).get_ordered_types(only_subclasses_of=(PurchasePickerModifier,)):
                if snippet.purchase_picker is not None and snippet.purchase_picker.guid64 == self.guid64:
                    yield from snippet.additional_purchase_items

    def attempt_payment_source_debit(self, total_debit, resolver):
        return self.payment_source.try_remove_funds(self.sim_info, total_debit, resolver=resolver)

    def attempt_payment_destination_credit(self, total_amount, resolver):
        if self.payment_destination is not None:
            pay_info = PaymentInfo(total_amount, resolver)
            return self.payment_destination.give_payment(pay_info)

    def _create_purchase_data(self):
        return PurchaseRowData()

    def _hook_additional_row_data(self, additional_data, purchase_item):
        pass

    def _hook_row_price(self, price, purchase_item, additional_data, resolver):
        """
        Modify the row price

        :param purchase_item: the purchase item tuning
        :param price: base_cost with default purchase item multipliers and global price multiplier
        :param resolver: the resolver that includes the actor and original target
        :return: price: the new price
        """
        return price

    def _hook_row_description(self, original_description, purchase_item, additional_data, resolver, obj=None):
        return original_description

    def _hook_obj_purchased(self, obj, purchase_row_data, price, resolver):
        """
        Modify the purchased object before it is delivered. All default effects have been
        applied at this point.

        :param obj: The spawned object
        :param purchase_row_data: The PurchaseRowData cached during picker_row_gen (including purchase item tuning, quality, base cost)
        :param price: The final price the sim has paid
        :param resolver: The resolver with the actor and the original target
        :return: None
        """
        pass

    def _hook_temporary_obj_created(self, obj, purchase_item, additional_data, quality_info=None):
        pass

    def _hook_on_picker_rows_gen(self):
        pass

    def _picker_rows_gen(self):
        resolver = self.get_resolver()

        global_price_multiplier = self.price_multiplier.get_multiplier(resolver)
        stock_manager = self.get_stock_manager()

        self._hook_on_picker_rows_gen()

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
                additional_data = picker_data.additional_data

                # Check the global visibility test for this row
                visibility_result = item.visibility_tests.run_tests(resolver)
                if not visibility_result:
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
                def _post_add(obj):
                    try:
                        if quality_info:
                            for state_value in quality_info.states:
                                if state_value is not None:
                                    obj.set_state(state_value.state, state_value, force_update=True)
                        self._hook_temporary_obj_created(obj, item, additional_data, quality_info=quality_info)
                    except:
                        logger.exception("Failed post_add on cached temp purchase picker object")

                if definition_data.recipe is not None:
                    temp_obj = create_craftable(definition_data.recipe, None, post_add=_post_add)
                else:
                    temp_obj = create_object(definition, post_add=_post_add)

                self._populated_objects.append(temp_obj)

                # Calculate price
                price = base_cost

                # Add quality_info multiplier
                if quality_info is not None:
                    price *= quality_info.static_price_multiplier

                # Add sim specific multipliers
                cost_multiplier = item.price_multiplier.get_multiplier(resolver)
                price = round(price * cost_multiplier * global_price_multiplier)

                price = self._hook_row_price(price, item, additional_data, resolver)

                # Check for discount
                is_discounted = item.show_discount and price < base_cost
                prediscounted_price = base_cost if is_discounted else None

                # Test if item should be disabled
                is_enabled = item.enable_tests.run_tests(resolver)

                # Get icon override
                icon_override = None
                # Override the icon with sold out icon
                if self.stock_management and self.stock_management.sold_out_icon is not None and current_stock == StockManager.STOCK_LEVEL_ZERO:
                    icon_override = IconInfoData(icon_resource=self.stock_management.sold_out_icon)

                # Get row name override
                if item.display_name_override is not None:
                    row_name = item.display_name_override(build_buy.get_object_catalog_name(definition.id))
                elif picker_data.custom_name is not None:
                    row_name = LocalizationHelperTuning.get_raw_text(picker_data.custom_name)
                else:
                    row_name = _create_localized_string(build_buy.get_object_catalog_name(definition.id))

                default_description = _create_localized_string(build_buy.get_object_catalog_description(definition.id))
                # Show disabled text override if not available to subject
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
                    row_description = self._hook_row_description(default_description, item, additional_data, resolver, obj=temp_obj)

                # Cache row info for immediate dialog response
                # Assumes dialog.purchase_by_object_ids is set to True.
                self.current_price_data[temp_obj.id] = (price, base_cost,)
                self.current_item_data[temp_obj.id] = picker_data

                row = PurchasePickerRow(def_id=definition.id, is_enable=is_enabled, objects={temp_obj},
                                        row_description=row_description, num_owned=0, num_available=current_stock,
                                        tags=category_tags, custom_price=price,
                                        icon_info_data_override=icon_override, show_discount=is_discounted,
                                        prediscounted_price=prediscounted_price)
                yield row

            return

        # Otherwise generate new rows
        for item in self.get_purchase_items_gen():
            # Check the global visibility test for this row
            visibility_result = item.visibility_tests.run_tests(resolver)
            if not visibility_result:
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

                    additional_data = AttributeDict()
                    self._hook_additional_row_data(additional_data, item)

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
                    quality_info = sims4.random.weighted_random_item(weighted_qualities) if len(weighted_qualities) > 0 else None

                    def _post_add(obj):
                        try:
                            if quality_info:
                                for state_value in quality_info.states:
                                    if state_value is not None:
                                        obj.set_state(state_value.state, state_value, force_update=True)
                            self._hook_temporary_obj_created(obj, item, additional_data, quality_info=quality_info)
                        except:
                            logger.exception("Failed post_add on cached temp purchase picker object")

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
                    price = base_cost

                    # Add quality_info multiplier
                    if quality_info is not None:
                        price *= quality_info.static_price_multiplier

                    # Add sim specific multipliers
                    cost_multiplier = item.price_multiplier.get_multiplier(resolver)
                    price = round(price * cost_multiplier * global_price_multiplier)

                    price = self._hook_row_price(price, item, additional_data, resolver)

                    # Check for discount
                    is_discounted = item.show_discount and price < base_cost
                    prediscounted_price = base_cost if is_discounted else None

                    # Test if item should be disabled
                    is_enabled = item.enable_tests.run_tests(resolver)

                    # Get icon override
                    icon_override = None
                    # Override the icon with sold out icon
                    if self.stock_management and self.stock_management.sold_out_icon is not None and current_stock == StockManager.STOCK_LEVEL_ZERO:
                        icon_override = IconInfoData(icon_resource=self.stock_management.sold_out_icon)

                    # Get Custom Name
                    custom_name = None
                    if item.custom_names is not None:
                        custom_name = random.choice(item.custom_names)

                    # Get row name override
                    if item.display_name_override is not None:
                        row_name = item.display_name_override(build_buy.get_object_catalog_name(definition.id))
                    elif custom_name is not None:
                        row_name = LocalizationHelperTuning.get_raw_text(custom_name)
                    else:
                        row_name = _create_localized_string(build_buy.get_object_catalog_name(definition.id))

                    # Get row description, fallback to object catalog description
                    default_description = _create_localized_string(build_buy.get_object_catalog_description(definition.id))

                    # Show disabled text override if not available to subject
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
                        row_description = self._hook_row_description(default_description, item, additional_data, resolver, obj=temp_obj)

                    # Cache item data
                    purchase_row_data = self._create_purchase_data()
                    purchase_row_data.base_cost = base_cost
                    purchase_row_data.category_tags = category_tags
                    purchase_row_data.custom_name = custom_name
                    purchase_row_data.definition = definition
                    purchase_row_data.definition_data = definition_data
                    purchase_row_data.purchase_item = item
                    purchase_row_data.purchase_item_source = item_source
                    purchase_row_data.quality = quality_info
                    purchase_row_data.stock_key = stock_key
                    purchase_row_data.additional_data = additional_data

                    # Cache row info for immediate dialog response
                    # Assumes dialog.purchase_by_object_ids is set to True.
                    self.current_price_data[temp_obj.id] = (price, base_cost,)
                    self.current_item_data[temp_obj.id] = purchase_row_data

                    # Cache picker row for future use
                    if stock_manager:
                        stock_manager.add_to_picker_cache(purchase_row_data)

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
                actor = resolver.get_participant(ParticipantTypeSingle.Actor)
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
                    price, base_cost = self.current_price_data[obj_id]
                    stock_key = purchase_data.stock_key

                    # Generate each item based on quantity purchased
                    for x in range(amount_to_purchase):
                        try:
                            # Attempt payment
                            if price > 0 and not self.attempt_payment_source_debit(price, resolver):
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
                                    try:
                                        if state_value is not None:
                                            obj.set_state(state_value.state, state_value)
                                    except:
                                        logger.exception("Failed setting state on final purchase picker object")

                            # Apply loot actions on object creation
                            obj_resolver = SingleActorAndObjectResolver(actor, obj, source='yourmom')
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

                            # Get "off-the-lot" Depreciation
                            depreciation_multiplier = purchase_data.purchase_item.depreciation_multiplier.get_multiplier(resolver)
                            if purchase_data.quality is not None:
                                depreciation_multiplier *= purchase_data.quality.static_depreciation_multiplier

                            # Set object value to purchase price
                            if purchase_data.purchase_item.use_base_cost_as_value:
                                obj_value = base_cost
                            else:
                                obj_value = price

                            # Apply depreciation
                            obj.current_value = obj_value * depreciation_multiplier

                            # Handle Object Purchased Hook
                            self._hook_obj_purchased(obj, purchase_data, price, resolver)

                            # Attempt to deliver object
                            if purchase_data.purchase_item.delivery_override is not None:
                                delivery_method = purchase_data.purchase_item.delivery_override
                            else:
                                delivery_method = self.delivery_method

                            if not delivery_method(resolver, obj, participant=self.owner_participant):
                                obj.destroy()
                                raise PurchaseException("DELIVERY_FAILED")

                            # Increment debit and purchase count
                            total_debit += price
                            purchase_count += 1

                            # Subtract from stock if managed
                            if stock_manager:
                                stock_manager.subtract_stock(stock_key)

                        except PurchaseException:
                            logger.exception("Delivery failed for purchase item with stock key: {}".format(stock_key))
                            # Aggregate failure count and stop looping if flagged to stop
                            if self.stop_on_first_failure:
                                failed_count = amount_to_purchase
                                break
                            # Increment failed count when an individual purchase fails
                            else:
                                failed_count += 1
                                continue

                if purchase_count > 0:
                    # Apply success loot
                    for loot in self.loot_on_success:
                        loot.apply_to_resolver(resolver)

                    # Give payment to payment_destinations
                    self.attempt_payment_destination_credit(total_debit, resolver)

                    # Show success notification
                    self._show_purchase_notification(self.purchase_success_notification, resolver, tokens=(purchase_count, failed_count, total_debit,))

                if failed_count > 0:
                    # Apply failure loot
                    for loot in self.loot_on_failure:
                        loot.apply_to_resolver(resolver)

                    # Show failure notification
                    self._show_purchase_notification(self.purchase_failed_notification, resolver, tokens=(purchase_count, failed_count, total_debit,))
        except:
            logger.exception("failed purchasing")
        finally:
            logger.debug("clearing purchase data")
            self.current_item_data.clear()
            self.current_price_data.clear()
            for obj in self._populated_objects:
                obj.destroy()
            self._populated_objects.clear()


@event_handler(CoreEvent.GAME_SERVICES_STARTED)
def _purchase_picker_services_on_game_services_started(*args, **kwargs):
    StockManager.clear_stock_managers()
