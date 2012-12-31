#!/usr/bin/env python

import mindcrack

import os.path
import json
import urllib
import urlparse

from datetime import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


VIDEOS_PER_PAGE = 30
INDEX = ''


def get_options(options):
    options = urlparse.parse_qs(options)

    if 'offset' in options:
        options['offset'] = int(options['offset'][0])

    if 'num_videos' in options:
        options['num_videos'] = int(options['num_videos'][0])

    # Filter is a non-optional option
    if 'filter' in options:
        options['filter'] = options['filter'][0].lower()
    else:
        options['filter'] = ''

    return options


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
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
        mindcrackers = self.mindcrack.mindcrackers()

        if self.get_cookie('mcnagg-options'):
            options = get_options(self.get_cookie('mcnagg-options'))
            videos = self.mindcrack.videos(**options)
        else:
            options = {'mindcrackers': [], 'filter': ''}
            videos = self.mindcrack.videos(num_videos=VIDEOS_PER_PAGE)

        self.render("body.html", videos=videos, mindcrackers=mindcrackers, checked=options['mindcrackers'], filter=options['filter'])


class VideosHandler(BaseHandler):
    def get(self):
        options = dict(
            mindcrackers=self.get_arguments('mindcrackers[]'),
            num_videos=int(self.get_argument('num-videos')),
            offset=int(self.get_argument('offset')),
            filter=self.get_argument('title-filter', default='')
        )

        videos = self.mindcrack.videos(**options)

        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None

        self.set_cookie('mcnagg-options', urllib.urlencode(options, True))
        self.write(json.dumps(videos, default=dthandler))
        self.finish()


class VideoModule(tornado.web.UIModule):
    def render(self, video):
        return self.render_string("modules/video.html", video=video)


class OptionsModule(tornado.web.UIModule):
    def render(self, mindcrackers, checked, filter):
        return self.render_string("modules/options.html", mindcrackers=mindcrackers, checked=checked, filter=filter)


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
