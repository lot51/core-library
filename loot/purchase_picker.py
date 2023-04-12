import services
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core import logger
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference


class OpenPurchasePickerLoot(BaseLootOperation):
    FACTORY_TUNABLES = {
        'purchase_picker': TunableReference(manager=services.get_instance_manager(Types.SNIPPET)),
    }

    def __init__(self, purchase_picker=None, **kwargs):
        self._purchase_picker = purchase_picker
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        try:
            picker = self._purchase_picker(resolver)
            picker.show_picker_dialog()
        except:
            logger.exception("Failed to open purchase picker: {}".format(self._purchase_picker))
