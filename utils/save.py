import services


def get_save_slot_guid():
    return str(services.get_persistence_service().get_save_slot_proto_guid())