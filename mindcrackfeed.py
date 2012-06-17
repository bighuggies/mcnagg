#!/usr/bin/env python

import database

import os.path
import json
import datetime

import tornado.auth
import tornado.database
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options


define("postgres_host", default="localhost:5432", help="database host")
define("postgres_database", default="mindcrackfeed", help="database name")
define("postgres_user", default="mindcrackfeedapp", help="database user")
define("postgres_password", default="lol", help="database password")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/filter", FilterHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={},
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
        videos = self.db.videos(num_videos=30)
        mindcrackers = self.db.mindcrackers()

        self.render("index.html", videos=videos, mindcrackers=mindcrackers)


class FilterHandler(BaseHandler):
    def get(self):
        mindcrackers = self.get_argument('mindcrackers', strip=True).split(',')
        videos = self.db.videos(mindcrackers=tuple(mindcrackers), num_videos=5)
        print videos[0]['uploaded'].isoformat()

        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

        self.write(json.dumps(videos, default=dthandler))
        self.finish()


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(os.environ.get('PORT', 5000))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
