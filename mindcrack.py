import json
import urllib2
import time
import datetime

from multiprocessing.pool import ThreadPool
from functools import wraps

_mindcrackers = sorted([
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
], key=lambda m: m['username'])

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
    return _mindcrackers


@memoize(timeout=300)
def videos(mindcrackers=[m['username'] for m in mindcrackers()], num_videos=1, offset=0, filter=''):
    pool = ThreadPool(processes=len(mindcrackers))
    pages = {mcer: 1 for mcer in mindcrackers}
    videos = {}

    for mcer in mindcrackers:
        pool.apply_async(_get_uploads, args=(mcer, pages[mcer]), callback=lambda r: videos.update(r))

    pool.close()
    pool.join()

    sorted_videos = []
    videos = {u: list(v) for u, v in videos.iteritems()}  # don't want to modify cache

    newest_mcer = mindcrackers[0]
    newest_vid = datetime.datetime(1,1,1)

    while len(sorted_videos) <= offset + num_videos:
        for mcer, uploads in videos.iteritems():
            if not uploads:
                continue

            if uploads[-1]['uploaded'] > newest_vid:
                newest_vid = uploads[-1]['uploaded']
                newest_mcer = mcer

        sorted_videos.append(videos[newest_mcer].pop())

        if not videos[newest_mcer]:
            pages[newest_mcer] += 1
            videos.update(_get_uploads(mcer, pages[mcer]))

        if not any(videos.values()):
            break

    return sorted_videos[offset:offset + num_videos]


@memoize(timeout=300)
def _get_uploads(username, page=1, filter=''):
    feed_url = 'https://gdata.youtube.com/feeds/api/users/{username}/uploads?v=2&alt=jsonc&start-index={offset}&max-results=50' \
        .format(username=username, offset=(50 * (page - 1)) + 1)

    feed = json.loads(urllib2.urlopen(feed_url).read())

    if feed['data']['totalItems'] <= 0 or feed['data']['totalItems'] < feed['data']['startIndex']:
        return {username: []}

    videos = [_process_video_data(item) for item in feed['data']['items']]

    if filter:
        videos = [video for video in videos if filter.lower() in video['title'].lower()]

    return {username: sorted(videos, key=lambda v: v['uploaded'])}


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
