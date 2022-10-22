import services
from situations.custom_states.custom_states_situation import CustomStatesSituation

class DefaultObjectCustomStatesSituation(CustomStatesSituation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_object = self._get_target_object()

    def _get_target_object(self):
        target_object = None
        default_target_id = self._seed.extra_kwargs.get('default_target_id', None)
        if default_target_id is not None:
            target_object = services.object_manager().get(default_target_id)
        return target_object

    def get_target_object(self):
        return self.target_object
