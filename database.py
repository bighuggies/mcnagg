import os
import json
import requests
import datetime
import psycopg2
from psycopg2 import extras


def _get_db():
    db_url = os.getenv('DATABASE_URL')
    conn = None

    if db_url:
        conn = psycopg2.connect('dbname=ddprh9d8b2m6av host=ec2-23-23-234-207.compute-1.amazonaws.com port=5432 user=mrkjurgyjpbrwt password=bRRcEKwPR7noC5yO0xMot1J7cL sslmode=require')
    else:
        conn = psycopg2.connect(database='mindcrackfeed', user='mindcrackfeedapp', password='lol')

    return conn


conn = _get_db()
cur = conn.cursor(cursor_factory=extras.RealDictCursor)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, cur)


def _youtube_feed(feed_id, number_videos=1, offset=1, orderby='published', feed_type='upload'):
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

    for item in feed['data']['items']:
        if type == 'playlist':
            item = item['video']

        video = dict(
            video_id=item['id'],
            title=item['title'],
            duration=item['duration'],
            uploader=item['uploader'],
            uploaded=datetime.datetime.strptime(item['uploaded'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            description=item['description'],
            thumbnail=item['thumbnail']['hqDefault']
        )

        yield video


def add_mindcracker(username, url):
    cur.execute('INSERT INTO mindcrackers VALUES (%s, %s);', (username.lower(), url.lower()))
    conn.commit()


def add_video(video_id, title, duration, uploader, uploaded, description, thumbnail):
    cur.execute('SELECT video_id FROM videos WHERE video_id=\'{}\''.format(video_id))
    if cur.fetchone() == None:
        cur.execute('INSERT INTO videos VALUES (%s, %s, %s, %s, %s, %s, %s);', (video_id, title, duration, uploader.lower(), uploaded, description, thumbnail))
    conn.commit()


def mindcrackers():
    cur.execute('SELECT * FROM mindcrackers')

    return [m for m in cur]


def videos(mindcrackers=tuple([m['username'] for m in mindcrackers()]), num_videos=15, offset=0):
    cur.execute('SELECT * FROM videos WHERE videos.uploader IN %s ORDER BY uploaded DESC LIMIT %s OFFSET %s', (mindcrackers, num_videos, offset))

    return [v for v in cur]


def main():
    for m in mindcrackers():
        for v in _youtube_feed(m, number_videos=50):
            add_video(**v)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
