import util

mindcrackersdict = [{'username': u'adlingtont', 'url': u'http://www.youtube.com/adlingtont', 'name': u'Adlington'}, {'username': u'bdoubleo100', 'url': u'http://www.youtube.com/bdoubleo100', 'name': u'BdoubleO'}, {'username': u'arkasmc', 'url': u'http://www.youtube.com/arkasmc', 'name': u'Arkas'}, {'username': u'ethoslab', 'url': u'http://www.youtube.com/ethoslab', 'name': u'EthosLab'}, {'username': u'jsano19', 'url': u'http://www.youtube.com/jsano19', 'name': u'Jsano'}, {'username': u'kurtjmac', 'url': u'http://www.youtube.com/kurtjmac', 'name': u'Kurtjmac'}, {'username': u'millbeeful', 'url': u'http://www.youtube.com/millbeeful', 'name': u'MillBee'}, {'username': u'nebris88', 'url': u'http://www.youtube.com/nebris88', 'name': u'Nebris'}, {'username': u'pauseunpause', 'url': u'http://www.youtube.com/pauseunpause', 'name': u'PauseUnpause'}, {'username': u'vintagebeef', 'url': u'http://www.youtube.com/vintagebeef', 'name': u'VintageBeef'}, {'username': u'shreeyamnet', 'url': u'http://www.youtube.com/shreeyamnet', 'name': u'Shreeyam'}, {'username': u'imanderzel', 'url': u'http://www.youtube.com/imanderzel', 'name': u'AnderZEL'}, {'username': u'w92baj', 'url': u'http://www.youtube.com/w92baj', 'name': u'Baj'}, {'username': u'docm77', 'url': u'http://www.youtube.com/docm77', 'name': u'DocM'}, {'username': u'guudeboulderfist', 'url': u'http://www.youtube.com/guudeboulderfist', 'name': u'Guude'}, {'username': u'justd3fy', 'url': u'http://www.youtube.com/justd3fy', 'name': u'JustDefy'}, {'username': u'supermcgamer', 'url': u'http://www.youtube.com/supermcgamer', 'name': u'MCGamer'}, {'username': u'mhykol', 'url': u'http://www.youtube.com/mhykol', 'name': u'Mhykol'}, {'username': u'pakratt13', 'url': u'http://www.youtube.com/pakratt13', 'name': u'Pakratt'}, {'username': u'pyropuncher', 'url': u'http://www.youtube.com/pyropuncher', 'name': u'PyroPuncher'}, {'username': u'thejims', 'url': u'http://www.youtube.com/thejims', 'name': u'TheJims'}, {'username': u'zisteau', 'url': u'http://www.youtube.com/zisteau', 'name': u'Zisteau'}, {'username': u'mindcracknetwork', 'url': u'http://www.youtube.com/mindcracknetwork', 'name': u'MindCrackNetwork'}, {'username': u'generikb', 'url': u'http://www.youtube.com/generikb', 'name': u'GenerikB'}]


def mindcrackers():
    return mindcrackersdict


def cached_videos(mindcrackers=tuple([m['username'] for m in mindcrackers()]), num_videos=1, offset=0):
    videos = []

    for m in mindcrackers:
        v = util.get_uploads(str(m), num_videos, offset)
        videos = videos + v

    return sorted(videos, key=lambda v: v['uploaded'])[offset:num_videos]


def videos(mindcrackers=tuple([m['username'] for m in mindcrackers()]), num_videos=1, offset=0):
    return cached_videos(mindcrackers, num_videos, offset)


def main():
    with open('m.txt', 'w') as f:
        for m in mindcrackers():
            f.write(m['username'] + ',' + m['name'] + '\n')


if __name__ == '__main__':
    main()
