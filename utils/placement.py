import services
import sims4
import random
from placement import ScoringFunctionRadial, create_starting_location, create_fgl_context_for_object, find_good_location
from routing import SurfaceType, SurfaceIdentifier


def _get_position_with_offset(starting_transform, starting_orientation, x_range=None, z_range=None):
    default_offset = sims4.math.Vector3(0, 0, 0)
    if x_range is not None:
        x_axis = starting_orientation.transform_vector(sims4.math.Vector3.X_AXIS())
        default_offset += x_axis * random.uniform(x_range.lower_bound, x_range.upper_bound)
    if z_range is not None:
        z_axis = starting_orientation.transform_vector(sims4.math.Vector3.Z_AXIS())
        default_offset += z_axis * random.uniform(z_range.lower_bound, z_range.upper_bound)
    offset = sims4.math.Transform(default_offset, sims4.math.Quaternion.IDENTITY())
    return sims4.math.Transform.concatenate(offset, starting_transform).translation, starting_orientation


def get_random_orientation():
    return sims4.random.random_orientation()


def get_location_near_location(obj, target_location, optimal_distance=0.5, radius_width=4, max_distance=8, random_orientation=False, x_range=None, z_range=None):
    _orientation = get_random_orientation()
    _routing_surface = target_location.routing_surface
    if _routing_surface is None:
        _routing_surface = SurfaceIdentifier(services.current_zone_id(), 0, SurfaceType.SURFACETYPE_WORLD)
    start_position, start_orientation = _get_position_with_offset(target_location.transform, _orientation, x_range=x_range, z_range=z_range)
    scoring_function = ScoringFunctionRadial(target_location.transform.translation, optimal_distance, radius_width, max_distance, _routing_surface)
    # location=target_location
    starting_location = create_starting_location(position=start_position, orientation=start_orientation, routing_surface=_routing_surface)
    fgl_context = create_fgl_context_for_object(starting_location, obj, max_distance=max_distance, scoring_functions=(scoring_function,))
    translation, orientation = find_good_location(fgl_context)
    return translation, _orientation, _routing_surface


def get_location_near_object(obj, target_obj, optimal_distance=0.5, radius_width=4, max_distance=8, random_orientation=False, x_range=None, z_range=None):
    if random_orientation:
        _orientation = get_random_orientation()
    else:
        _orientation = target_obj.orientation
    _routing_surface = target_obj.routing_surface
    start_position, start_orientation = _get_position_with_offset(target_obj.location.transform, _orientation, x_range=x_range, z_range=z_range)
    scoring_function = ScoringFunctionRadial(target_obj.location.transform.translation, optimal_distance, radius_width, max_distance, _routing_surface)
    # position=target_obj.position
    starting_location = create_starting_location(position=start_position, orientation=start_orientation, routing_surface=_routing_surface)
    fgl_context = create_fgl_context_for_object(starting_location, obj, max_distance=max_distance, scoring_functions=(scoring_function,))
    translation, orientation = find_good_location(fgl_context)

    return translation, _orientation, _routing_surface