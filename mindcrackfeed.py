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


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/about", AboutHandler),
            (r"/videos", VideosHandler),
            (r"/fetch", FetchVideos)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Video": VideoModule, "Options": OptionsModule},
            # xsrf_cookies=True,
            # cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            # login_url="/auth/login",
            autoescape=None,
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = database


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class HomeHandler(BaseHandler):
    def get(self):
        self.render("index.html")


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
            self.write('fetching new videos ')
            self.flush()

            for m in self.db.mindcrackers():
                self.write('fetching ' + m['username'] + '\'s videos ')
                self.flush()

                for v in util.youtube_feed(m['username'], number_videos=3):
                    self.db.add_video(**v)

            self.write('rendering template ')
            self.flush()

            videos = self.db.videos(num_videos=videos_per_page)
            mindcrackers = self.db.mindcrackers()

            with open('templates/index.html', 'w') as f:
                f.write(self.render_string("body.html", videos=videos, mindcrackers=mindcrackers))

            self.write('done')
            self.finish()
        else:
            self.write_error(401)


class VideoModule(tornado.web.UIModule):
    def render(self, video):
        return self.render_string("modules/video.html", video=video)


class OptionsModule(tornado.web.UIModule):
    def render(self, mindcrackers):
        return self.render_string("modules/options.html", mindcrackers=mindcrackers)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(os.environ.get('PORT', 5000))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
