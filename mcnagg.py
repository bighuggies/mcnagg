#!/usr/bin/env python

import mindcrack

import os.path
import json
import urllib
import urlparse

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


def get_options(options):
    options = urlparse.parse_qs(options)

    if 'offset' in options:
        options['offset'] = int(options['offset'][0])

    # Filter is a non-optional option
    if 'title_filter' in options:
        options['title_filter'] = options['title_filter'][0].lower()
    else:
        options['title_filter'] = ''

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
            ui_modules={"Video": VideoModule, "Options": OptionsModule,
                        "Twitter": TwitterModule, "Reddit": RedditModule},
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
            options['offset'] = 0

            videos = self.mindcrack.videos(**options)
        else:
            options = {'mindcrackers': [], 'title_filter': ''}
            videos = self.mindcrack.videos()

        self.render("body.html", videos=videos, mindcrackers=mindcrackers,
                    checked=options['mindcrackers'], title_filter=options['title_filter'])


class VideosHandler(BaseHandler):
    def get(self):
        options = dict(
            mindcrackers=self.get_arguments('mindcrackers[]'),
            offset=int(self.get_argument('offset')),
            title_filter=self.get_argument('title_filter', default='')
        )

        videos = self.mindcrack.videos(**options)

        self.set_cookie('mcnagg-options', urllib.urlencode(options, True))
        self.write(json.dumps([v.serialize() for v in videos]))
        self.finish()


class VideoModule(tornado.web.UIModule):
    def render(self, video):
        return self.render_string("modules/video.html", video=video)


class OptionsModule(tornado.web.UIModule):
    def render(self, mindcrackers, checked, title_filter):
        return self.render_string("modules/options.html", mindcrackers=mindcrackers, checked=checked, title_filter=title_filter)


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
