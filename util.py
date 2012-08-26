from datetime import datetime, timedelta

import pylibmc
import requests
import json
import math

CACHE_SLICE_SIZE = 30


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


def get_uploads(feed_id, number_videos=1, offset=0):
    print("Getting " + str(number_videos) + " videos for " + feed_id)

    mc = pylibmc.Client(['127.0.0.1'])

    keys = [str(x) for x in xrange(0, number_videos, CACHE_SLICE_SIZE) if x < number_videos]
    cached = mc.get_multi(keys, key_prefix=feed_id)


    videos = []

    for i in keys:
        try:
            videos = videos + cached[i]
        except KeyError:
            vs = []
            for v in youtube_feed(feed_id, CACHE_SLICE_SIZE, int(i) + 1):
                vs.append(v)

            videos = videos + vs

            mc.set(feed_id + i, vs, time=300)
    
    return videos[offset:number_videos]


def youtube_feed(feed_id, number_videos=1, offset=1, feed_type='upload'):
    if feed_type == 'show':
        feed_url = 'https://gdata.youtube.com/feeds/api/seasons/{feed_id}/episodes?v=2&alt=jsonc&start-index={offset}&max-results={number_videos}'.format(
            feed_id=feed_id, offset=offset, number_videos=number_videos)
    elif feed_type == 'playlist':
        feed_url = 'http://gdata.youtube.com/feeds/api/playlists/{feed_id}?v=2&alt=jsonc&start-index={offset}&max-results={number_videos}'.format(
            feed_id=feed_id, offset=offset, number_videos=number_videos)
    elif feed_type == 'upload':
        feed_url = 'https://gdata.youtube.com/feeds/api/users/{username}/uploads?v=2&alt=jsonc&start-index={offset}&max-results={number_videos}'.format(
            username=feed_id, offset=offset, number_videos=number_videos)
    else:
        raise ValueError('Type <' + feed_type + '> is not a valid feed type. Valid types are <"upload">, <"playlist"> or <"show">.')

    if number_videos > 50:
        raise ValueError('Only allowed to get a maximum of 50 videos per request from YouTube')

    feed = json.loads(requests.get(feed_url).text)

    if feed['data']['totalItems'] > 0 and feed['data']['totalItems'] > feed['data']['startIndex']:
        for item in feed['data']['items']:
            if type == 'playlist':
                item = item['video']

            yield _process_video_data(item)


def youtube_video_data(video_id, raw=False):
    raw_video = json.loads(requests.get('https://gdata.youtube.com/feeds/api/videos/{0}?v=2&alt=jsonc'.format(video_id)).text)
    print raw_video

    if 'error' in raw_video:
        raise IOError('No such video')

    if raw:
        return raw_video
    else:
        return _process_video_data(raw_video['data'])


def _process_video_data(video_data):
    return dict(
        video_id=video_data['id'],
        title=video_data['title'],
        duration=video_data['duration'],
        uploader=video_data['uploader'],
        uploaded=datetime.strptime(video_data['uploaded'], "%Y-%m-%dT%H:%M:%S.%fZ"),
        description=video_data['description'],
        thumbnail=video_data['thumbnail']['hqDefault']
    )
