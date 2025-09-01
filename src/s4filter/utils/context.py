import game_services
import services


class Context:
    def __init__(self, zone):
        self.zone = zone

    @property
    def sim_now(self):
        return services.time_service().sim_now

    @property
    def game_now(self):
        return services.game_clock_service().now()

    @property
    def in_world_edit_mode(self):
        return self.zone and self.zone.venue_service.build_buy_edit_mode

    @property
    def is_traveling(self):
        return game_services.service_manager.is_traveling

    @property
    def save_slot_id(self):
        return str(services.get_persistence_service().get_save_slot_proto_guid())

    @property
    def save_slot_name(self):
        save_proto = services.get_persistence_service().get_save_slot_proto_buff()
        return save_proto.slot_name

    @staticmethod
    def get_current_context():
        zone = services.current_zone()
        return Context(zone)

