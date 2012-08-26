from datetime import datetime, timedelta
import os
import json
import math

import pylibmc
import requests

CACHE_SLICE_SIZE = 30
MINDCRACKERS = [{'username': u'adlingtont', 'url': u'http://www.youtube.com/adlingtont', 'name': u'Adlington'}, {'username': u'bdoubleo100', 'url': u'http://www.youtube.com/bdoubleo100', 'name': u'BdoubleO'}, {'username': u'arkasmc', 'url': u'http://www.youtube.com/arkasmc', 'name': u'Arkas'}, {'username': u'ethoslab', 'url': u'http://www.youtube.com/ethoslab', 'name': u'EthosLab'}, {'username': u'jsano19', 'url': u'http://www.youtube.com/jsano19', 'name': u'Jsano'}, {'username': u'kurtjmac', 'url': u'http://www.youtube.com/kurtjmac', 'name': u'Kurtjmac'}, {'username': u'millbeeful', 'url': u'http://www.youtube.com/millbeeful', 'name': u'MillBee'}, {'username': u'nebris88', 'url': u'http://www.youtube.com/nebris88', 'name': u'Nebris'}, {'username': u'pauseunpause', 'url': u'http://www.youtube.com/pauseunpause', 'name': u'PauseUnpause'}, {'username': u'vintagebeef', 'url': u'http://www.youtube.com/vintagebeef', 'name': u'VintageBeef'}, {'username': u'shreeyamnet', 'url': u'http://www.youtube.com/shreeyamnet', 'name': u'Shreeyam'}, {'username': u'imanderzel', 'url': u'http://www.youtube.com/imanderzel', 'name': u'AnderZEL'}, {'username': u'w92baj', 'url': u'http://www.youtube.com/w92baj', 'name': u'Baj'}, {'username': u'docm77', 'url': u'http://www.youtube.com/docm77', 'name': u'DocM'}, {'username': u'guudeboulderfist', 'url': u'http://www.youtube.com/guudeboulderfist', 'name': u'Guude'}, {'username': u'justd3fy', 'url': u'http://www.youtube.com/justd3fy', 'name': u'JustDefy'}, {'username': u'supermcgamer', 'url': u'http://www.youtube.com/supermcgamer', 'name': u'MCGamer'}, {'username': u'mhykol', 'url': u'http://www.youtube.com/mhykol', 'name': u'Mhykol'}, {'username': u'pakratt13', 'url': u'http://www.youtube.com/pakratt13', 'name': u'Pakratt'}, {'username': u'pyropuncher', 'url': u'http://www.youtube.com/pyropuncher', 'name': u'PyroPuncher'}, {'username': u'thejims', 'url': u'http://www.youtube.com/thejims', 'name': u'TheJims'}, {'username': u'zisteau', 'url': u'http://www.youtube.com/zisteau', 'name': u'Zisteau'}, {'username': u'mindcracknetwork', 'url': u'http://www.youtube.com/mindcracknetwork', 'name': u'MindCrackNetwork'}, {'username': u'generikb', 'url': u'http://www.youtube.com/generikb', 'name': u'GenerikB'}]


# mc = pylibmc.Client(
#     servers=[os.environ.get('MEMCACHIER_SERVERS', '')],
#     username=os.environ.get('MEMCACHIER_USERNAME', ''),
#     password=os.environ.get('MEMCACHIER_PASSWORD', ''),
#     binary=True
# )

mc = pylibmc.Client(['127.0.0.1'])


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


def mindcrackers():
    return MINDCRACKERS


def videos(mindcrackers=[m['username'] for m in mindcrackers()], num_videos=1, offset=0):
    videos = []

    for m in mindcrackers:
        v = get_uploads(str(m), num_videos+offset, 0)
        videos = videos + v

    return sorted(videos, key=lambda v: v['uploaded'], reverse=True)[offset:num_videos + offset]


def get_uploads(username, num_videos=1, offset=0):
    max_index = num_videos + offset
    keys = [str(x) for x in xrange(offset, max_index, CACHE_SLICE_SIZE)]
    
    print('Getting videos for ' + username + ' from ' + str(offset) + ' to ' + str(max_index))

    cached = mc.get_multi(keys, key_prefix=username)
    videos = []

    for i in keys:
        try:
            videos = videos + cached[i]
        except KeyError:
            vs = youtube_feed(username, CACHE_SLICE_SIZE, int(i))
            videos = videos + vs

            mc.set(username + i, vs, time=300)

    return videos[offset:max_index]


def youtube_feed(feed_id, num_videos=1, offset=0, feed_type='upload'):
    if feed_type == 'show':
        feed_url = 'https://gdata.youtube.com/feeds/api/seasons/{feed_id}/episodes?v=2&alt=jsonc&start-index={offset}&max-results={num_videos}'.format(
            feed_id=feed_id, offset=offset+1, num_videos=num_videos)
    elif feed_type == 'playlist':
        feed_url = 'http://gdata.youtube.com/feeds/api/playlists/{feed_id}?v=2&alt=jsonc&start-index={offset}&max-results={num_videos}'.format(
            feed_id=feed_id, offset=offset+1, num_videos=num_videos)
    elif feed_type == 'upload':
        feed_url = 'https://gdata.youtube.com/feeds/api/users/{username}/uploads?v=2&alt=jsonc&start-index={offset}&max-results={num_videos}'.format(
            username=feed_id, offset=offset+1, num_videos=num_videos)
    else:
        raise ValueError('Type <' + feed_type + '> is not a valid feed type. Valid types are <"upload">, <"playlist"> or <"show">.')

    if num_videos > 50:
        raise ValueError('Only allowed to get a maximum of 50 videos per request from YouTube')

    feed = json.loads(requests.get(feed_url).text)

    items = []
    if feed['data']['totalItems'] > 0 and feed['data']['totalItems'] > feed['data']['startIndex']:
        for item in feed['data']['items']:
            if type == 'playlist':
                item = item['video']

            items.append(_process_video_data(item))

    return items


def youtube_video_data(video_id, raw=False):
    raw_video = json.loads(requests.get('https://gdata.youtube.com/feeds/api/videos/{0}?v=2&alt=jsonc'.format(video_id)).text)

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
