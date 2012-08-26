#!/usr/bin/env python

import mindcrack

import os.path
import json

from datetime import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


VIDEOS_PER_PAGE = 30
INDEX = ''


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/about", AboutHandler),
            (r"/videos", VideosHandler)
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

        self.mindcrack = mindcrack


class BaseHandler(tornado.web.RequestHandler):
    @property
    def mindcrack(self):
        return self.application.mindcrack


class HomeHandler(BaseHandler):
    def get(self):
        if self.settings['debug'] == True:
            videos = self.mindcrack.videos(num_videos=VIDEOS_PER_PAGE)
            mindcrackers = self.mindcrack.mindcrackers()

            self.render("body.html", videos=videos, mindcrackers=mindcrackers)
        else:
            if INDEX == "":
                self.write('Down for maintenance, please check back in 5 minutes')
                self.finish()
            else:
                self.write(INDEX)
                self.finish()


class AboutHandler(BaseHandler):
    def get(self):
        self.render("about.html")


class VideosHandler(BaseHandler):
    def get(self):
        mindcrackers = self.get_arguments('mindcrackers[]')
        num_videos = int(self.get_argument('num-videos'))
        offset = int(self.get_argument('offset'))

        videos = self.mindcrack.videos(mindcrackers=mindcrackers, num_videos=num_videos, offset=offset)

        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None

        self.write(json.dumps(videos, default=dthandler))
        self.finish()


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
