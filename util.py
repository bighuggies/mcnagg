from datetime import datetime, timedelta

import requests
import json
import math


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


def youtube_feed(feed_id, number_videos=1, offset=1, orderby='published', feed_type='upload'):
    if feed_type == 'show':
        feed_url = 'https://gdata.youtube.com/feeds/api/seasons/{feed_id}/episodes?v=2&alt=jsonc&start-index={offset}&max-results={number_videos}&orderby={orderby}'.format(
            feed_id=feed_id, offset=offset, number_videos=number_videos, orderby=orderby)
    elif feed_type == 'playlist':
        feed_url = 'http://gdata.youtube.com/feeds/api/playlists/{feed_id}?v=2&alt=jsonc&start-index={offset}&max-results={number_videos}&orderby={orderby}'.format(
            feed_id=feed_id, offset=offset, number_videos=number_videos, orderby=orderby)
    elif feed_type == 'upload':
        feed_url = 'https://gdata.youtube.com/feeds/api/users/{username}/uploads?v=2&alt=jsonc&start-index={offset}&max-results={number_videos}&orderby={orderby}'.format(
            username=feed_id, offset=offset, number_videos=number_videos, orderby=orderby)
    else:
        raise ValueError('Type <' + feed_type + '> is not a valid feed type. Valid types are <upload>, <playlist> or <show>.')

    feed = json.loads(requests.get(feed_url).text)

    if feed['data']['totalItems'] > 0:
        for item in feed['data']['items']:
            if type == 'playlist':
                item = item['video']

            video = dict(
                video_id=item['id'],
                title=item['title'],
                duration=item['duration'],
                uploader=item['uploader'],
                uploaded=datetime.strptime(item['uploaded'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                description=item['description'],
                thumbnail=item['thumbnail']['hqDefault']
            )

            yield video
