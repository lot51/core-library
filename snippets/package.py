from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, Tunable, TunableList


class PackageSnippet(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=get_instance_manager(Types.SNIPPET)):
    INSTANCE_TUNABLES = {
        'mod_name': Tunable(tunable_type=str, default='N/A'),
        'creator_name': Tunable(tunable_type=str, default='N/A'),
        'version': Tunable(tunable_type=str, default='1.0.0'),
        'required_modules': TunableList(tunable=Tunable(tunable_type=str, default='')),
    }

    __slots__ = ('mod_name', 'creator_name', 'version',)

    def __repr__(self):
        return '<PackageSnippet> {} by {}; version {};'.format(self.mod_name, self.creator_name, self.version)