from gdata.youtube.service import YouTubeService
from datetime import date
import iso8601


mindcrackers = ['adlingtont', 'ImAnderZEL', 'ArkasMc', 'W92Baj', 'BdoubleO100',
                # 'docm77', 'EthosLab', 'GuudeBoulderfist', 'JSano19',
                # 'JustD3fy', 'kurtjmac', 'SuperMCGamer', 'Mhykol', 'nebris88',
                # 'pakratt13', 'PauseUnpause', 'Pyropuncher', 'ShreeyamNET',
                'thejims', 'VintageBeef', 'Zisteau']


def GetAndPrintVideoFeed(uri):
    yt_service = YouTubeService()
    feed = yt_service.GetYouTubeVideoFeed(uri)
    for entry in feed.entry:
        PrintEntryDetails(entry)  # full documentation for this function


def PrintEntryDetails(entry):
    # print 'Video title: %s' % entry.media.title.text
    # print 'Video description: %s' % entry.media.description.text
    print 'Video author: %s' % entry.author[0].name.text
    print 'Video author link: %s' % entry.author[0].uri.text
    # print 'Video published: %s' % entry.published.text
    # print 'Video watch page: %s' % entry.media.player.url
    # print 'Video duration: %s' % entry.media.duration.seconds
    # print entry.media.thumbnail[0]

    # print iso8601.parse_date(entry.published.text)


if __name__ == '__main__':
    for user in mindcrackers:
        uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?max-results=1' % user
        GetAndPrintVideoFeed(uri)
