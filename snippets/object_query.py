import services
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference


class ObjectQuerySnippet(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):
    INSTANCE_TUNABLES = {
        'object_source': ObjectSearchMethodVariant(),
    }
