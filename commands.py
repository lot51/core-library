from server_commands.argument_helpers import TunableInstanceParam
from sims4.commands import Command, CommandType, output
from sims4.resources import Types


@Command('purchase_picker.refresh', command_type=CommandType.Live)
def refresh_purchase_picker(purchase_picker:TunableInstanceParam(Types.SNIPPET), _connection=None):
    if purchase_picker is not None:
        stock_manager = purchase_picker.get_stock_manager()
        stock_manager._refresh_required = True
        output('Successfully refreshed picker stock: {}'.format(purchase_picker.__name__), _connection)