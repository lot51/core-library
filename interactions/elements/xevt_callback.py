from element_utils import build_critical_section
from elements import ParentElement


class CallbackXevtElement(ParentElement):
    def __init__(self, interaction, sequence, xevt_id, callback=None):
        super().__init__()
        self._interaction = interaction
        self._sequence = sequence
        self._callback = callback
        self._xevt_id = xevt_id
        self._xevt_handle = None

    def _run_xevt(self, timeline):
        if self._callback is not None:
            self._callback()

    def _run(self, timeline):
        sequence = self._sequence

        def register_xevt(_):
            self._xevt_handle = self._interaction.animation_context.register_event_handler(lambda _: self._run_xevt(timeline), handler_id=self._xevt_id)

        def release_xevt(_):
            self._xevt_handle.release()
            self._xevt_handle = None

        sequence = build_critical_section(register_xevt, sequence, release_xevt)
        return timeline.run_child(sequence)

