#!/usr/bin/env python

import database

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
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Video": VideoModule, "Options": OptionsModule},
            # xsrf_cookies=True,
            # cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            # login_url="/auth/login",
            autoescape=None,
            debug=False
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = database


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class HomeHandler(BaseHandler):
    def get(self):
        videos = self.db.videos(num_videos=videos_per_page)
        mindcrackers = self.db.mindcrackers()

        self.render("body.html", videos=videos, mindcrackers=mindcrackers)


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
