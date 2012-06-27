#!/usr/bin/env python

import database
import util

import os.path
import json

from datetime import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


videos_per_page = 30
index = ''


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/about", AboutHandler),
            (r"/videos", VideosHandler),
            (r"/fetch", FetchVideos),
            (r"/update", UpdateVideos)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Video": VideoModule, "Options": OptionsModule, "Twitter": TwitterModule, "Reddit": RedditModule},
            # xsrf_cookies=True,
            # cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            # login_url="/auth/login",
            autoescape=None,
            debug=True
        )

        if os.environ.get('ENVIRONMENT') == 'heroku':
            settings['debug'] = False

        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = database


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class HomeHandler(BaseHandler):
    def get(self):
        if self.settings['debug'] == True:
            videos = self.db.videos(num_videos=videos_per_page)
            mindcrackers = self.db.mindcrackers()

            self.render("body.html", videos=videos, mindcrackers=mindcrackers)
        else:
            if index == "":
                self.write('Down for maintenance, please check back in 5 minutes')
                self.finish()
            else:
                self.write(index)
                self.finish()


class AboutHandler(BaseHandler):
    def get(self):
        self.render("about.html")


class VideosHandler(BaseHandler):
    def get(self):
        mindcrackers = self.get_arguments('mindcrackers[]')
        num_videos = self.get_argument('num-videos')
        offset = self.get_argument('offset')

        videos = self.db.videos(mindcrackers=tuple(mindcrackers), num_videos=num_videos, offset=offset)

        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None

        self.write(json.dumps(videos, default=dthandler))
        self.finish()


class FetchVideos(BaseHandler):
    def get(self):
        try:
            self.get_argument('auth')
        except:
            self.write_error(401)

        if self.get_argument('auth') == 'm1ndcr4ckf33d4pp':
            self.write('[' + str(datetime.utcnow()) + ']')
            self.write(' fetching new videos ')
            self.flush()

            for m in self.db.mindcrackers():
                self.write('fetching ' + m['username'] + '\'s videos ')
                self.flush()

                for v in util.youtube_feed(m['username'], number_videos=30):
                    self.db.add_video(**v)

            self.write('rendering template ')
            self.flush()

            videos = self.db.videos(num_videos=videos_per_page)
            mindcrackers = self.db.mindcrackers()

            global index
            index = self.render_string("body.html", videos=videos, mindcrackers=mindcrackers)

            self.write('done fetching ')
            self.write('[' + str(datetime.utcnow()) + ']')

            self.finish()
        else:
            self.write_error(401)


class UpdateVideos(BaseHandler):
    def get(self):
        try:
            self.get_argument('auth')
        except:
            self.write_error(401)

        if self.get_argument('auth') == 'm1ndcr4ckf33d4pp':
            self.write('[' + str(datetime.utcnow()) + ']')
            self.write(' updating videos')
            self.flush()

            for video in self.db.videos(num_videos=100):
                try:
                    video = util.youtube_video_data(video['video_id'])
                    self.write(' updating ' + video['title'])
                    self.flush()
                    self.db.update_video(**video)
                except:
                    self.write(' culling ' + video['title'])
                    self.flush()
                    self.db.remove_video(video['video_id'])

            self.write(' done updating ')
            self.write('[' + str(datetime.utcnow()) + ']')

            self.finish()

        else:
            self.write_error(401)


class VideoModule(tornado.web.UIModule):
    def render(self, video):
        return self.render_string("modules/video.html", video=video)


class OptionsModule(tornado.web.UIModule):
    def render(self, mindcrackers):
        return self.render_string("modules/options.html", mindcrackers=mindcrackers)


class TwitterModule(tornado.web.UIModule):
    def render(self):
        return self.render_string("modules/twitter.html")


class RedditModule(tornado.web.UIModule):
    def render(self):
        return self.render_string("modules/reddit.html")


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(os.environ.get('PORT', 5000))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
