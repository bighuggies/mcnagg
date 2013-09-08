import math
import time

from datetime import datetime, timedelta
from functools import wraps


def get_fancy_time(date):
    seconds = (datetime.utcnow() - date).total_seconds()

    if seconds < 0:
        return 'Some time in the future'

    seconds = seconds
    minutes = seconds / 60
    hours = seconds / 60 / 60
    days = seconds / 60 / 60 / 24
    months = days / 30

    deltas = [('second', seconds), ('minute', minutes), ('hour', hours), ('day', days), ('month', months)]

    fuzzy_delta = ('second', 0)
    plural = False

    for unit, delta in deltas:
        if math.floor(delta) > 0:
            fuzzy_delta = (unit, int(math.floor(delta)))

    if fuzzy_delta[1] > 1:
        plural = True

    return '{delta} {unit}{plural} ago'.format(delta=fuzzy_delta[1], unit=fuzzy_delta[0], plural='s' if plural else '')


def get_HMS(time):
    hms = str(timedelta(seconds=time))
    parts = hms.split(':')

    if parts[0] == '0':
        return ':'.join(parts[1:])
    else:
        return hms


def memoize(timeout=60):
    def memoized(func):
        cache = {}

        @wraps(func)
        def memoizer(*args, **kwargs):
            curtime = time.time()
            key = str(args) + str(kwargs)

            if key not in cache:
                cache[key] = {
                    'value': func(*args, **kwargs), 'timestamp': curtime}
            elif curtime - cache[key]['timestamp'] > timeout:
                del cache[key]
                cache[key] = {
                    'value': func(*args, **kwargs), 'timestamp': curtime}

            return cache[key]['value']

        return memoizer
    return memoized
