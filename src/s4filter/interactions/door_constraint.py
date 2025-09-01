from interactions.constraints import ZoneConstraintMixin, FrontDoorOption, Nowhere, Circle, Cone
from sims4.tuning.tunable import TunableSingletonFactory, Tunable, TunableEnumEntry
from singletons import DEFAULT


class TunedDoorConstraint(ZoneConstraintMixin):

    def __init__(self, radius, ideal_radius, line_of_sight, front_door_position_option):
        super().__init__()
        self._radius = radius
        self._ideal_radius = ideal_radius
        self._line_of_sight = line_of_sight
        self._front_door_position_option = front_door_position_option

    def create_zone_constraint(self, sim, target=None, routing_surface=DEFAULT, **kwargs):
        front_door = target
        if front_door is not None and hasattr(front_door, 'get_door_positions'):
            (front_position, back_position) = front_door.get_door_positions()
            if self._front_door_position_option == FrontDoorOption.OUTSIDE_FRONT_DOOR:
                position = front_position
            else:
                position = back_position
            routing_surface = front_door.routing_surface
        else:
            return Nowhere('Front Door Constraint: Could not find a door for this constraint.')
        los_factory = self._line_of_sight()
        los_factory.generate(position, routing_surface)
        los_constraint = los_factory.constraint
        circle_constraint = Circle(position, self._line_of_sight.max_line_of_sight_radius, routing_surface=routing_surface, ideal_radius=self._ideal_radius)
        return circle_constraint.intersect(los_constraint)


class TunableDoorConstraint(TunableSingletonFactory):
    FACTORY_TYPE = TunedDoorConstraint

    def __init__(self, description='A tunable type for creating a constraint inside or outside the front door', callback=None, **kwargs):
        from objects.components.line_of_sight_component import TunableLineOfSightFactory
        super().__init__(
            radius=Tunable(description='circle radius', tunable_type=float, default=2),
            ideal_radius=Tunable(description='ideal distance for this front door constraint, points closer to the ideal distance will score higher.', tunable_type=float, default=2),
            line_of_sight=TunableLineOfSightFactory(description='Tuning to generate a light of sight constraint either inside or outside the front door in order to get the sims to move there.'),
            front_door_position_option=TunableEnumEntry(description='The option of whether to use the inside or outside side of the front door in order to generate the constraint.', tunable_type=FrontDoorOption, default=FrontDoorOption.OUTSIDE_FRONT_DOOR),
            description=description,
            **kwargs
        )
