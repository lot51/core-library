import random
import math

from lot51_core import logger


def range_by(start, stop, step=1):
    n = int(round((stop - start)/float(step)))
    if n > 1:
        return([start + step*i for i in range(n+1)])
    elif n == 1:
        return ([start])
    else:
        return([])


def chance_succeeded(chance):
    roll = random.random()
    if chance is 0 or roll is 0:
        return False
    return roll <= chance


def circular_coordinates_gen(radius=1, angle=45, precision=3):
    for i in range_by(0, (360-angle), angle):
        a = math.radians(i)
        x = radius * math.cos(a)
        y = radius * math.sin(a)
        yield round(x, precision), round(y, precision)


def circular_coordinates_by_count_gen(radius=1, count=6, precision=3):
    angle = 360/count
    for i in range(count):
        a = math.radians(i*angle)
        x = radius * math.cos(a)
        y = radius * math.sin(a)
        yield round(x, precision), round(y, precision)


def flatten_weighted_list(pairs, flipped=False):
     value_index = 0 if flipped else 1
     return [item[value_index] for item in pairs]


def weighted_sort(pairs, flipped=False, flatten=True, descending=True):
    weight_index = 1 if flipped else 0
    sorted_pairs = sorted(pairs, key=lambda item: random.random() * item[weight_index], reverse=descending)
    if not flatten:
        return sorted_pairs
    return flatten_weighted_list(sorted_pairs, flipped=flipped)
