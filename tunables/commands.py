import services
import sims4.commands
from interactions import ParticipantTypeSingle, ParticipantType
from sims4.resources import Types
from sims4.tuning.tunable import TunableVariant, Tunable, TunableEnumEntry, TunableTuple, HasTunableSingletonFactory, \
    TunableList, AutoFactoryInit
from lot51_core import logger as core_logger


class TunableCommandArgumentVariant(TunableVariant):
    def __init__(self, **kwargs):
        super().__init__(
                boolean=Tunable(
                    tunable_type=bool,
                    default=False
                ),
                string=Tunable(
                    tunable_type=str,
                    default=''
                ),
                num_float=Tunable(
                    tunable_type=float,
                    default=0.0
                ),
                num_int=Tunable(
                    tunable_type=int,
                    default=0
                ),
                instance=TunableTuple(
                    tuning_id=Tunable(
                        tunable_type=int,
                        default=0
                    ),
                    tunable_type=TunableEnumEntry(
                        tunable_type=Types,
                        default=Types.INVALID
                    )
                ),
                participant=TunableEnumEntry(
                    tunable_type=ParticipantTypeSingle,
                    default=ParticipantTypeSingle.Actor
                ),
                participants=TunableEnumEntry(
                    tunable_type=ParticipantType,
                    default=ParticipantType.Actor
                ),
                **kwargs
        )


class TunableCommand(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'command': Tunable(
            tunable_type=str,
            default='',
            description="The command string to run",
        ),
        'arguments': TunableList(
            description="A list of arguments to pass to the command.",
            tunable=TunableCommandArgumentVariant(),
        ),
        'client_command': Tunable(
            tunable_type=bool,
            default=False,
            description="If True, this command will attempt to run on the client. Otherwise it will run a simulation command."
        ),
    }

    __slots__ = ('command', 'arguments', 'client_command',)

    @classmethod
    def apply_to_resolver(cls, resolver, logger=None):
        try:
            if logger is None:
                logger = core_logger
            args = cls.get_args(resolver)
            full_command = '{}'.format(cls.command)
            full_command += ''.join([' {}'] * len(args)).format(*args)
            logger.info('running command: {}'.format(full_command))
            client_id = services.client_manager().get_first_client_id()
            if cls.client_command:
                sims4.commands.client_cheat(full_command, client_id)
            else:
                sims4.commands.execute(full_command, client_id)
            return True
        except Exception as e:
            logger.exception('failed to execute command')
        return False

    @classmethod
    def get_args(cls, resolver):
        arguments_with_participants = list()
        for argument in cls.arguments:
            if isinstance(argument, ParticipantTypeSingle):
                participant_list = resolver.get_participants(argument)
                arguments_with_participants.append(participant_list[0] if participant_list else None)
            elif isinstance(argument, ParticipantType):
                participant_list = tuple([participant.get_sim_instance() if participant.is_sim else participant
                                          for participant in resolver.get_participants(argument)
                                          if participant is not None])
                arguments_with_participants.append(participant_list)
            elif hasattr(argument, 'tunable_type'):
                manager = services.get_instance_manager(argument.tunable_type)
                instance = manager.get(argument.tuning_id)
                arguments_with_participants.append(instance)
            else:
                arguments_with_participants.append(argument)
        return arguments_with_participants