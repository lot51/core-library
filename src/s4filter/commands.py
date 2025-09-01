import json
import logging
import services
from event_testing.resolver import DoubleObjectResolver
from lot51_core import logger
from lot51_core.utils.os import open_url_in_browser
from lot51_core.utils.save_based_config import instanced_configs
from server_commands.argument_helpers import TunableInstanceParam
from sims4.commands import Command, CommandType, output
from sims4.resources import Types


@Command('purchase_picker.refresh', command_type=CommandType.Live)
def command_refresh_purchase_picker(purchase_picker:TunableInstanceParam(Types.SNIPPET), _connection=None):
    if purchase_picker is not None:
        stock_manager = purchase_picker.get_stock_manager()
        stock_manager._refresh_required = True
        output('Successfully refreshed picker stock: {}'.format(purchase_picker.__name__), _connection)


@Command('purchase_picker.open', command_type=CommandType.Live)
def command_open_purchase_picker(purchase_picker:TunableInstanceParam(Types.SNIPPET), _connection=None):
    try:
        if purchase_picker is not None:
            sim = services.get_active_sim()
            resolver = DoubleObjectResolver(sim, sim)
            picker = purchase_picker(resolver)
            picker.show_picker_dialog()
        else:
            logger.error("[command][purchase_picker.open] Unable to find purchase picker snippet")
    except:
        logger.exception("[command][purchase_picker.open] Failed to open purchase picker")


@Command("lot51_core.open_url", command_type=CommandType.Live)
def command_on_version_dialog_response(base_url:str=None, params:str=None, _connection=None):
    if params is not None:
        params = json.loads(params)
    else:
        params = dict()
    open_url_in_browser(base_url, **params)


@Command("lot51_core.toggle_debug", command_type=CommandType.Live)
def command_toggle_debug_logging(_connection=None):
    if logger.level == logging.DEBUG:
        mode = 'off'
        logger.setLevel(logging.INFO)
    else:
        mode = 'on'
        logger.setLevel(logging.DEBUG)

    output("Logging Debug Mode: {}".format(mode), _connection)


@Command("lot51_core.config_debug", command_type=CommandType.Live)
def command_print_config_debug(_connection=None):
    output("Save Based Configs:", _connection)
    for config in instanced_configs:
        output("Name: {}, Household Name: {}".format(config.config_name, config.household_name), _connection)
