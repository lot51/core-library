from sims4.tuning.instances import create_tuning_blueprint_class


def create_tuning_blueprint(base_class, name):
    tuning_blueprint_cls = create_tuning_blueprint_class(base_class)
    tuning_blueprint = tuning_blueprint_cls(name)
    return tuning_blueprint