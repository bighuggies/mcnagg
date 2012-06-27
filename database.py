import psycopg2
from psycopg2 import extras


def _get_db():
    # db_url = os.getenv('DATABASE_URL')
    # conn = None

    # if db_url:
    #     conn = psycopg2.connect('dbname=ddprh9d8b2m6av host=ec2-23-23-234-207.compute-1.amazonaws.com port=5432 user=mrkjurgyjpbrwt password=bRRcEKwPR7noC5yO0xMot1J7cL sslmode=require')
    # else:
    #     conn = psycopg2.connect(database='mindcrackfeed', user='mindcrackfeedapp', password='lol')
    conn = psycopg2.connect('\
        dbname=ddprh9d8b2m6av \
        host=ec2-23-23-234-207.compute-1.amazonaws.com \
        port=5432 user=mrkjurgyjpbrwt \
        password=bRRcEKwPR7noC5yO0xMot1J7cL sslmode=require')
    return conn


conn = _get_db()
cur = conn.cursor(cursor_factory=extras.RealDictCursor)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, cur)


def add_video(video_id, title, duration, uploader, uploaded, description, thumbnail):
    cur.execute('SELECT video_id FROM videos WHERE video_id=\'{}\''.format(video_id))

    if cur.fetchone() == None:
        cur.execute('INSERT INTO videos VALUES (%s, %s, %s, %s, %s, %s, %s);',
            (video_id, title, duration, uploader.lower(), uploaded, description, thumbnail))

        conn.commit()
    else:
        update_video(video_id, title, duration, uploader, uploaded, description, thumbnail)


def update_video(video_id, title, duration, uploader, uploaded, description, thumbnail):
    cur.execute('UPDATE videos SET \
        title=%s, \
        duration=%s, \
        uploaded=%s, \
        description=%s, \
        thumbnail=%s \
        WHERE video_id=%s', (title, duration, uploaded, description, thumbnail, video_id))

    conn.commit()


def remove_video(video_id=None):
    if video_id:
        cur.execute('DELETE FROM videos WHERE video_id=%s', (video_id, ))

    conn.commit()


def add_mindcracker(username, name, url):
    cur.execute('INSERT INTO mindcrackers VALUES (%s, %s, %s);', (username.lower(), url.lower(), name,))
    conn.commit()


def mindcrackers():
    cur.execute('SELECT * FROM mindcrackers')

    return [m for m in cur]


def videos(mindcrackers=tuple([m['username'] for m in mindcrackers()]), num_videos=1, offset=0):
    if mindcrackers:
        cur.execute('SELECT * FROM videos, mindcrackers \
            WHERE videos.uploader IN %s \
            AND videos.uploader = mindcrackers.username \
            ORDER BY uploaded DESC LIMIT %s OFFSET %s',
            (mindcrackers, num_videos, offset))

        return [v for v in cur]

    return []


def main():
    with open('m.txt', 'w') as f:
        for m in mindcrackers():
            f.write(m['username'] + ',' + m['name'] + '\n')


if __name__ == '__main__':
    main()
