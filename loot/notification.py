from interactions.utils.loot_basic_op import BaseLootOperation
import services
from lot51_core import logger
from ui.ui_dialog_notification import UiDialogNotification


class SingleNotification(BaseLootOperation):
    FACTORY_TUNABLES = {
        'notification': UiDialogNotification.TunableFactory(description='Display a notification targeting the active sim'),
    }

    def __init__(self, notification=None,**kwargs):
        super().__init__(**kwargs)
        self._notification = notification

    def _apply_to_subject_and_target(self, subject, target, resolver):
        try:
            owner = services.get_active_sim()
            # owner_resolver = owner.get_resolver()
            dialog = self._notification(owner, resolver)
            dialog.show_dialog()
        except:
            logger.exception("Failed showing notification")
