import json
import urllib2
import time
import datetime

from collections import deque
from multiprocessing.pool import ThreadPool
from functools import wraps

MINDCRACKERS = [
    {'username': u'adlingtont', 'url': u'http://www.youtube.com/adlingtont', 'name': u'Adlington'},
    {'username': u'avidyazen', 'url': u'http://www.youtube.com/avidyazen', 'name': u'Avidya'},
    {'username': u'bdoubleo100', 'url': u'http://www.youtube.com/bdoubleo100', 'name': u'BdoubleO'},
    {'username': u'arkasmc', 'url': u'http://www.youtube.com/arkasmc', 'name': u'Arkas'},
    {'username': u'ethoslab', 'url': u'http://www.youtube.com/ethoslab', 'name': u'EthosLab'},
    {'username': u'jsano19', 'url': u'http://www.youtube.com/jsano19', 'name': u'Jsano'},
    {'username': u'kurtjmac', 'url': u'http://www.youtube.com/kurtjmac', 'name': u'Kurtjmac'},
    {'username': u'millbeeful', 'url': u'http://www.youtube.com/millbeeful', 'name': u'MillBee'},
    {'username': u'nebris88', 'url': u'http://www.youtube.com/nebris88', 'name': u'Nebris'},
    {'username': u'pauseunpause', 'url': u'http://www.youtube.com/pauseunpause', 'name': u'PauseUnpause'},
    {'username': u'vintagebeef', 'url': u'http://www.youtube.com/vintagebeef', 'name': u'VintageBeef'},
    {'username': u'shreeyamnet', 'url': u'http://www.youtube.com/shreeyamnet', 'name': u'Shreeyam'},
    {'username': u'imanderzel', 'url': u'http://www.youtube.com/imanderzel', 'name': u'AnderZEL'},
    {'username': u'w92baj', 'url': u'http://www.youtube.com/w92baj', 'name': u'Baj'},
    {'username': u'docm77', 'url': u'http://www.youtube.com/docm77', 'name': u'DocM'},
    {'username': u'guudeboulderfist', 'url': u'http://www.youtube.com/guudeboulderfist', 'name': u'Guude'},
    {'username': u'blamethecontroller', 'url': u'http://www.youtube.com/BlameTheController', 'name': u'BlameTheController'},
    {'username': u'supermcgamer', 'url': u'http://www.youtube.com/supermcgamer', 'name': u'MCGamer'},
    {'username': u'mhykol', 'url': u'http://www.youtube.com/mhykol', 'name': u'Mhykol'},
    {'username': u'pakratt13', 'url': u'http://www.youtube.com/pakratt13', 'name': u'Pakratt'},
    {'username': u'pyropuncher', 'url': u'http://www.youtube.com/pyropuncher', 'name': u'PyroPuncher'},
    {'username': u'thejims', 'url': u'http://www.youtube.com/thejims', 'name': u'TheJims'},
    {'username': u'zisteau', 'url': u'http://www.youtube.com/zisteau', 'name': u'Zisteau'},
    {'username': u'mindcracknetwork', 'url': u'http://www.youtube.com/mindcracknetwork', 'name': u'MindCrack Network'},
    {'username': u'generikb', 'url': u'http://www.youtube.com/generikb', 'name': u'GenerikB'},
    {'username': u'paulsoaresjr', 'url': u'http://www.youtube.com/paulsoaresjr', 'name': u'PaulSoaresJR'},
    {'username': u'vechz', 'url': u'http://www.youtube.com/vechz', 'name': u'Vechs'}
]

def memoize(timeout=60):
    def memoized(func):
        cache = {}

        @wraps(func)
        def memoizer(*args, **kwargs):
            curtime = time.time()
            key = str(args) + str(kwargs)

            if key not in cache:
                cache[key] = {'value': func(*args, **kwargs), 'timestamp': curtime}
            elif curtime - cache[key]['timestamp'] > timeout:
                del cache[key]
                cache[key] = {'value': func(*args, **kwargs), 'timestamp': curtime}

            return cache[key]['value']

        return memoizer
    return memoized


def mindcrackers():
    return sorted(MINDCRACKERS, key=lambda m: m['username'])


@memoize(timeout=300)
def videos(mindcrackers=[m['username'] for m in mindcrackers()], num_videos=1, offset=0, filter=''):
    pool = ThreadPool(processes=len(mindcrackers))
    q = deque()

    for mcer in mindcrackers:
        pool.apply_async(_get_uploads, args=(mcer, num_videos, offset), callback=lambda r: q.extend(r))

    pool.close()
    pool.join()

    return sorted(list(q), key=lambda v: v['uploaded'], reverse=True)[offset:num_videos + offset]

def _get_uploads(username, num_videos=1, offset=0, filter=''):
    videos = _youtube_feed(username, num_videos, offset)

    if filter:
        videos = [video for video in videos if filter.lower() in video['title'].lower()]

    return videos[offset:num_videos + offset]


def _youtube_feed(feed_id, num_videos=1, offset=0):
    num_videos = 50 if num_videos > 50 else num_videos

    feed_url = 'https://gdata.youtube.com/feeds/api/users/{username}/uploads?v=2&alt=jsonc&start-index={offset}&max-results={num_videos}' \
        .format(username=feed_id, offset=offset + 1, num_videos=num_videos)

    feed = json.loads(urllib2.urlopen(feed_url).read())

    if feed['data']['totalItems'] <= 0:
        return []

    return [_process_video_data(item) for item in feed['data']['items']]


def _process_video_data(video_data):
    return dict(
        video_id=video_data['id'],
        title=video_data['title'],
        duration=video_data['duration'],
        uploader=video_data['uploader'],
        uploaded=datetime.datetime.strptime(video_data['uploaded'], "%Y-%m-%dT%H:%M:%S.%fZ"),
        description=video_data['description'],
        thumbnail=video_data['thumbnail']['hqDefault']
    )
