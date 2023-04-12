import services
from situations.create_and_use_object_situation import TARGET_OBJECT_TOKEN
from situations.custom_states.custom_states_situation import CustomStatesSituation


class DefaultObjectCustomStatesSituation(CustomStatesSituation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_object = self._get_target_object()

    def _get_target_object(self):
        reader = self._seed.custom_init_params_reader
        if reader is None:
            target_object_id = self._seed.extra_kwargs.get('default_target_id', None)
        else:
            target_object_id = reader.read_uint64(TARGET_OBJECT_TOKEN, None)
        if target_object_id:
            return services.object_manager().get(target_object_id)

    def get_target_object(self):
        return self.target_object

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        if self.target_object is not None:
            writer.write_uint64(TARGET_OBJECT_TOKEN, self.target_object.id)
