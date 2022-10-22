import random


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