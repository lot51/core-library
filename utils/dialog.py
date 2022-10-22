from collections import namedtuple
import services
from ui.ui_dialog import UiDialogResponse, ButtonType
from ui.ui_dialog_notification import UiDialogNotification
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory
from sims4.localization import LocalizationHelperTuning, _create_localized_string
from ui.ui_dialog_generic import UiDialogTextInputOk, UiDialogOkCancel
from ui.ui_text_input import UiTextInput
from sims4.collections import AttributeDict

class TextInputLength(HasTunableSingletonFactory, AutoFactoryInit):
    __qualname__ = 'Text Input Length'

    def build_msg(self, dialog, msg, *additional_tokens):
        msg.max_length = 255
        msg.min_length = 0
        msg.input_too_short_tooltip = LocalizationHelperTuning.get_raw_text('Text is too short')


def create_input(title="", input_text="", restricted_characters=None, max_length=255):
    localized_title = lambda **_: LocalizationHelperTuning.get_raw_text(title)
    localized_text_placeholder = lambda **_: LocalizationHelperTuning.get_raw_text(input_text)
    text_input = UiTextInput(sort_order=0, restricted_characters=restricted_characters, height=0)
    text_input.default_text = localized_text_placeholder
    text_input.title = localized_title
    text_input.initial_value = localized_text_placeholder
    text_input.check_profanity = False
    text_input.max_length = max_length
    text_input.length_restriction = TextInputLength()
    return text_input


def create_translated_input(title="", input_text="", restricted_characters=None, max_length=255):
    localized_title = lambda **_: LocalizationHelperTuning.get_raw_text(title)
    # localized_text_placeholder = lambda **_: _create_localized_string(input_text)
    localized_text_placeholder = lambda **_: LocalizationHelperTuning.get_raw_text(input_text)
    text_input = UiTextInput(sort_order=0, restricted_characters=restricted_characters, height=0)
    text_input.default_text = localized_text_placeholder
    text_input.title = localized_title
    text_input.initial_value = localized_text_placeholder
    text_input.check_profanity = False
    text_input.max_length = max_length
    text_input.length_restriction = TextInputLength()
    return text_input


class DialogHelper:
    UiDialogNotificationVisualType = UiDialogNotification.UiDialogNotificationVisualType
    UiDialogNotificationUrgency = UiDialogNotification.UiDialogNotificationUrgency
    UiDialogUiRequest = UiDialogResponse.UiDialogUiRequest
    UiDialogNotificationExpandBehavior = UiDialogNotification.UiDialogNotificationExpandBehavior

    class CharacterRestriction:
        NUMBERS = lambda *_: _create_localized_string(0x8FE40C44)

    @staticmethod
    def create_notification(title="", text="", primary_icon=None, urgency=UiDialogNotification.UiDialogNotificationUrgency.DEFAULT, visual_type=UiDialogNotification.UiDialogNotificationVisualType.INFORMATION, expand_behavior=UiDialogNotification.UiDialogNotificationExpandBehavior.USER_SETTING, ui_responses=()):
        return UiDialogNotification.TunableFactory().default(
            None,
            title=lambda *args, **kwargs: title,
            text=lambda *args, **kwargs: text,
            visual_type=visual_type,
            urgency=urgency,
            icon=primary_icon,
            information_level=UiDialogNotification.UiDialogNotificationLevel.PLAYER,
            ui_responses=ui_responses,
            expand_behavior=expand_behavior,
        )

    @staticmethod
    def get_raw_text(text):
        return LocalizationHelperTuning.get_raw_text(text)

    @staticmethod
    def get_lambda(localized_str):
        return lambda *_, **__: localized_str

    @staticmethod
    def create_dialog(title="", description="", button_text="Okay", callback=None):
        client = services.client_manager().get_first_client()
        localized_title = lambda **_: LocalizationHelperTuning.get_raw_text(title)
        localized_text = lambda **_: LocalizationHelperTuning.get_raw_text(description)
        dialog = UiDialogOkCancel.TunableFactory().default(
            client.active_sim,
            text=localized_text,
            title=localized_title,
            text_ok=lambda **_: LocalizationHelperTuning.get_raw_text(button_text),
            is_special_dialog=False
        )
        if callback:
            dialog.add_listener(callback)
        return dialog

    @staticmethod
    def create_text_dialog(title="", description="", input_title="", input_text="", button_text="Okay", callback=None):
        client = services.client_manager().get_first_client()
        localized_title = lambda **_: LocalizationHelperTuning.get_raw_text(title)
        localized_text = lambda **_: LocalizationHelperTuning.get_raw_text(description)

        primary_input = create_translated_input(input_title, input_text)

        inputs = AttributeDict({'primary': primary_input})
        dialog = UiDialogTextInputOk.TunableFactory().default(
            client.active_sim,
            text=localized_text,
            title=localized_title,
            text_inputs=inputs,
            text_ok=lambda **_: LocalizationHelperTuning.get_raw_text(button_text),
            is_special_dialog=False
        )
        if callback:
            dialog.add_listener(callback)

        return dialog

    @staticmethod
    def create_command(command_name, *args):
        command = namedtuple('Command', ('command', 'arguments'))
        return command(command_name, args)

    @staticmethod
    def build_ui_response(response_id=ButtonType.DIALOG_RESPONSE_NO_RESPONSE, text=None, subtext=None, ui_request=UiDialogUiRequest.NO_REQUEST, response_command=None):
        return UiDialogResponse(dialog_response_id=response_id, text=text, subtext=subtext, ui_request=ui_request, response_command=response_command)
