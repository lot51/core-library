import uuid
import services
from lot51_core.tunables.purchase_item import TunablePurchaseItem
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableReference, TunableList


class PurchasePickerModifier(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):
    INSTANCE_TUNABLES = {
        'purchase_picker': TunableReference(
            description="The PurchasePickerSnippet to modify.",
            manager=services.get_instance_manager(Types.SNIPPET),
        ),
        'additional_purchase_items': TunableList(
            tunable=TunablePurchaseItem.TunableFactory(),
        )
    }

    @classmethod
    def _tuning_loaded_callback(cls):
        for row in cls.additional_purchase_items:
            if row.stock_id is None:
                row.stock_id = str(uuid.uuid4())
