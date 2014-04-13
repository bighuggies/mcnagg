import json
import urllib2
import datetime
import heapq
import itertools

import util

from multiprocessing.pool import ThreadPool
from collections import deque

_mindcrackers = sorted([
    {'username': u'adlingtont', 'url':
        u'http://www.youtube.com/adlingtont', 'name': u'Adlington'},
    {'username': u'avidyazen', 'url':
        u'http://www.youtube.com/avidyazen', 'name': u'Avidya'},
    {'username': u'bdoubleo100', 'url':
        u'http://www.youtube.com/bdoubleo100', 'name': u'BdoubleO'},
    {'username': u'arkasmc', 'url':
        u'http://www.youtube.com/arkasmc', 'name': u'Arkas'},
    {'username': u'ethoslab', 'url':
        u'http://www.youtube.com/ethoslab', 'name': u'EthosLab'},
    {'username': u'jsano19', 'url':
        u'http://www.youtube.com/jsano19', 'name': u'Jsano'},
    {'username': u'kurtjmac', 'url':
        u'http://www.youtube.com/kurtjmac', 'name': u'Kurtjmac'},
    {'username': u'millbeeful', 'url':
        u'http://www.youtube.com/millbeeful', 'name': u'MillBee'},
    {'username': u'nebris88', 'url':
        u'http://www.youtube.com/nebris88', 'name': u'Nebris'},
    {'username': u'pauseunpause', 'url':
        u'http://www.youtube.com/pauseunpause', 'name': u'PauseUnpause'},
    {'username': u'vintagebeef', 'url':
        u'http://www.youtube.com/vintagebeef', 'name': u'VintageBeef'},
    {'username': u'shreeyamnet', 'url':
        u'http://www.youtube.com/shreeyamnet', 'name': u'Shreeyam'},
    {'username': u'imanderzel', 'url':
        u'http://www.youtube.com/imanderzel', 'name': u'AnderZEL'},
    {'username': u'w92baj', 'url':
        u'http://www.youtube.com/w92baj', 'name': u'Baj'},
    {'username': u'docm77', 'url':
        u'http://www.youtube.com/docm77', 'name': u'DocM'},
    {'username': u'guudeboulderfist', 'url':
        u'http://www.youtube.com/guudeboulderfist', 'name': u'Guude'},
    {'username': u'blamethecontroller', 'url':
        u'http://www.youtube.com/BlameTheController', 'name': u'BlameTheController'},
    {'username': u'supermcgamer', 'url':
        u'http://www.youtube.com/supermcgamer', 'name': u'MCGamer'},
    {'username': u'mhykol', 'url':
        u'http://www.youtube.com/mhykol', 'name': u'Mhykol'},
    {'username': u'pakratt13', 'url':
        u'http://www.youtube.com/pakratt13', 'name': u'Pakratt'},
    {'username': u'pyropuncher', 'url':
        u'http://www.youtube.com/pyropuncher', 'name': u'PyroPuncher'},
    {'username': u'thejims', 'url':
        u'http://www.youtube.com/thejims', 'name': u'TheJims'},
    {'username': u'zisteau', 'url':
        u'http://www.youtube.com/zisteau', 'name': u'Zisteau'},
    {'username': u'mindcracknetwork', 'url':
        u'http://www.youtube.com/mindcracknetwork', 'name': u'MindCrack Network'},
    {'username': u'generikb', 'url':
        u'http://www.youtube.com/generikb', 'name': u'GenerikB'},
    {'username': u'paulsoaresjr', 'url':
        u'http://www.youtube.com/paulsoaresjr', 'name': u'PaulSoaresJR'},
    {'username': u'vechz', 'url':
        u'http://www.youtube.com/vechz', 'name': u'Vechs'},
    {'username': u'sethbling', 'url':
        u'http://www.youtube.com/sethbling', 'name': u'SethBling'}
], key=lambda m: m['username'])


def mindcrackers():
    return _mindcrackers


def videos(mindcrackers=[m['username'] for m in mindcrackers()], num_videos=1, offset=0, title_filter=''):
    pool = ThreadPool(processes=len(mindcrackers))
    uploads = deque()

    for mcer in mindcrackers:
        pool.apply_async(_video_generator, args=(mcer, title_filter), callback=lambda r: uploads.append(r))

    pool.close()
    pool.join()

    return list(itertools.islice(heapq.merge(*uploads), offset, offset + num_videos))


def _video_generator(username, title_filter=''):
    page = 1
    videos = []

    while True:
        if not videos:
            videos.extend(_get_uploads(username, page, title_filter))
            page += 1

        yield videos.pop()


@util.memoize(timeout=300)
def _get_uploads(username, page, title_filter=''):
    feed_url = 'https://gdata.youtube.com/feeds/api/users/{username}/uploads?v=2&alt=jsonc&start-index={offset}&max-results=50' \
        .format(username=username, offset=(50 * (page - 1)) + 1)

    feed = json.loads(urllib2.urlopen(feed_url).read())

    if feed['data']['totalItems'] <= 0 or feed['data']['totalItems'] < feed['data']['startIndex']:
        raise StopIteration("No videos")
    else:
        videos = [Video(item) for item in feed['data']['items'] if title_filter.lower() in item['title'].lower()]

    if not videos:
        raise StopIteration("No matching videos")

    return list(reversed(videos))


class Video(object):
    video_id = ""
    title = ""
    duration = 0
    uploader = ""
    uploaded = None
    description = ""
    thumbnail = None

    def __init__(self, raw_data):
        super(Video, self).__init__()
        self.process_raw_video(raw_data)

    def process_raw_video(self, raw_data):
        self.video_id = raw_data['id']
        self.title = raw_data['title']
        self.duration = raw_data['duration']
        self.uploader = raw_data['uploader']
        self.uploaded = datetime.datetime.strptime(
            raw_data['uploaded'], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.description = raw_data['description']
        self.thumbnail = raw_data['thumbnail']['hqDefault']

    def serialize(self):
        return {
            "video_id": self.video_id,
            "title": self.title,
            "duration": self.duration,
            "uploader": self.uploader,
            "uploaded": self.uploaded.isoformat(),
            "description": self.description,
            "thumbnail": self.thumbnail
        }

    def __eq__(self, other):
        return self.uploaded == other.uploaded

    def __gt__(self, other):
        # This is reversed because heapq.merge expects iterators to be
        # ascending
        return self.uploaded < other.uploaded

    def __str__(self):
        return self.title + " " + self.uploader

    def __repr__(self):
        return self.__str__()
