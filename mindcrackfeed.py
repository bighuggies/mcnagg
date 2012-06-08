import os
from gdata.youtube.service import YouTubeService
import iso8601
import datetime
from flask import Flask
from flask import render_template

mindcrackers = ['adlingtont', 'ImAnderZEL', 'ArkasMc', 'W92Baj', 'BdoubleO100',
                'docm77', 'EthosLab', 'GuudeBoulderfist', 'JSano19', 'JustD3fy',
                'kurtjmac', 'SuperMCGamer', 'Mhykol', 'nebris88', 'pakratt13',
                'PauseUnpause', 'Pyropuncher', 'ShreeyamNET', 'thejims',
                'VintageBeef', 'Zisteau']


app = Flask(__name__)


# mindcrackers = ['docm77']
# videos = [{'author_uri': 'https://www.youtube.com/user/docm77', 'view_count': '192', 'thumbnails': ['http://i.ytimg.com/vi/Gb66dn9NcPY/0.jpg'], 'author': 'docm77', 'url': 'https://www.youtube.com/watch?v=-IgWKcX8h7Y&feature=youtube_gdata_player', 'title': u'Docm77s Gametime - Saints Row: The Third [HD] #33', 'published': datetime.datetime(2012, 6, 7), 'duration': '1434', 'description': 'This is a playthrough of Saints Row: The Third on PC ;-)\n'}]


@app.route('/')
def hello():
    yt_service = YouTubeService()
    videos = []

    for user in mindcrackers:
        uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?max-results=1' % user
        feed = yt_service.GetYouTubeVideoFeed(uri)
        entry = feed.entry[0]

        video = dict(
            title=unicode(entry.media.title.text, errors='ignore'),
            author=entry.author[0].name.text,
            author_uri='https://www.youtube.com/user/{0}'.format(entry.author[0].name.text),
            published=iso8601.parse_date(entry.published.text),
            description=unicode(entry.media.description.text, errors='ignore'),
            url=entry.media.player.url,
            duration=entry.media.duration.seconds,
            view_count=entry.statistics.view_count,
            thumbnail=entry.media.thumbnail[0].url
        )

        videos.append(video)

    return render_template('index.html', videos=videos)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
