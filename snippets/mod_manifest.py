import importlib
import json
import services
from lot51_core import logger
from lot51_core.services.events import event_handler, CoreEvent
from lot51_core.utils.dialog import DialogHelper
from lot51_core.utils.semver import Version
from sims4.common import Pack, are_packs_available
from sims4.localization import TunableLocalizedStringFactory
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import Tunable, TunableMapping, OptionalTunable, HasTunableReference, TunableTuple, TunableEnumSet
from ui.ui_dialog import CommandArgType


class ModManifest(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):
    did_notify = False

    INSTANCE_TUNABLES = {
        'creator_name': Tunable(tunable_type=str, default='N/A', description="Creator name of this mod"),
        'mod_name': Tunable(tunable_type=str, default='N/A', description="Name of this mod"),
        'version': Tunable(tunable_type=str, default='1.0.0', description="A semver version pattern that represents the current package version."),
        'module_path': OptionalTunable(
            description="Module path to lookup script version. __version__ must be defined in __init__.py in the root of the module. Must follow semver pattern.",
            tunable=Tunable(tunable_type=str, default=None, allow_empty=True)
        ),
        'required_packs': TunableEnumSet(enum_type=Pack, default_enum_list=(Pack.BASE_GAME,)),
        'version_mismatch_notification': OptionalTunable(
            tunable=TunableTuple(
                title=TunableLocalizedStringFactory(description="The title displayed in the notification. Use {0.String} to include the mod name, {1.String} for the creator name."),
                text=TunableLocalizedStringFactory(description="The text displayed in the notification. Use {0.String} to include the script version, {1.String} for the package version, {2.String} for the mod name, {3.String} for the creator name."),
                http=OptionalTunable(
                    description="Enable to display a button that links to your website with optional query params appended.",
                    tunable=TunableTuple(
                        base_url=Tunable(tunable_type=str, default='https://lot51.cc', description="Base website url"),
                        params=TunableMapping(
                            description="Query parameters added to the base_url when a player clicks button in the Version Mismatch notification",
                            key_type=Tunable(tunable_type=str, default=''),
                            value_type=Tunable(tunable_type=str, default=''),
                        ),
                        button_text=TunableLocalizedStringFactory(),
                    )
                ),
            )
        )
    }

    __slots__ = ('creator_name', 'mod_name', 'version', 'version_mismatch_notification', 'module_path', 'required_packs',)

    @classmethod
    def to_str(cls):
        return '<ModManifest {} by {} ({}); version {}>'.format(cls.mod_name, cls.creator_name, cls.__name__, cls.version)

    @classmethod
    def _tuning_loaded_callback(cls):
        logger.info('[tuning_loaded_callback] {}'.format(cls.to_str()))

    @classmethod
    def all_snippets_gen(cls):
        yield from services.get_instance_manager(Types.SNIPPET).get_ordered_types(only_subclasses_of=ModManifest)

    @classmethod
    def get_module(cls):
        try:
            if cls.module_path is not None:
                mod = importlib.import_module(cls.module_path)
                if mod is not None:
                    return mod
        except:
            logger.debug("Could not import module: {} for manifest: {}".format(cls.module_path, cls.__name__))
            return None

    @classmethod
    def are_packs_available(cls):
        return are_packs_available(cls.required_packs)

    @classmethod
    def get_package_version(cls):
        return Version.parse(cls.version, optional_minor_and_patch=True)

    @classmethod
    def get_script_version(cls):
        mod = cls.get_module()
        if mod is not None:
            return Version.parse(mod.__version__, optional_minor_and_patch=True)

    @classmethod
    def check_version_and_notify(cls):
        if cls.version_mismatch_notification is not None:
            if not cls.did_notify:
                script_ver = cls.get_script_version()
                package_ver = cls.get_package_version()
                if script_ver != package_ver:
                    dialog = cls._build_version_tns(script_ver, package_ver)
                    dialog.show_dialog()
                cls.did_notify = True

    @classmethod
    def _build_version_tns(cls, script_ver, package_ver):
        title = cls.version_mismatch_notification.title(cls.mod_name, cls.creator_name)
        text = cls.version_mismatch_notification.text(str(script_ver), str(package_ver), cls.mod_name, cls.creator_name)

        ui_responses = list()
        if cls.version_mismatch_notification.http is not None:
            ui_button_text = cls.version_mismatch_notification.http.button_text
            arg0 = DialogHelper.create_arg(CommandArgType.ARG_TYPE_STRING, cls.version_mismatch_notification.http.base_url)
            arg1 = DialogHelper.create_arg(CommandArgType.ARG_TYPE_STRING, json.dumps(dict(cls.version_mismatch_notification.http.params)))
            response_command = DialogHelper.create_command("lot51_core.open_url", arg0, arg1)
            ui_responses.append(DialogHelper.build_ui_response(response_id=DialogHelper.ButtonType.DIALOG_RESPONSE_OK, text=ui_button_text, ui_request=DialogHelper.UiDialogUiRequest.SEND_COMMAND, response_command=response_command))

        dialog = DialogHelper.create_notification(title=title, text=text, urgency=DialogHelper.UiDialogNotificationUrgency.URGENT, expand_behavior=DialogHelper.UiDialogNotificationExpandBehavior.FORCE_EXPAND, ui_responses=ui_responses)
        return dialog


@event_handler(CoreEvent.LOADING_SCREEN_LIFTED)
def _process_mod_manifests(*args, **kwargs):
    for snippet in ModManifest.all_snippets_gen():
        try:
            snippet.check_version_and_notify()
        except:
            logger.exception("Failed processing mod manifest: {}".format(snippet))
