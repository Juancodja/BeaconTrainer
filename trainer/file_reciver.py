"""Usage: python file_receiver.py
Demonstrates a server that receives a multipart-form-encoded set of files in an
HTTP POST, or streams in the raw data of a single file in an HTTP PUT.
See file_uploader.py in this directory for code that uploads files in this format.
"""

import logging

try:
    from urllib.parse import unquote
except ImportError:
    # Python 2.
    from urllib import unquote

import tornado.ioloop
import tornado.web
from tornado import options


# my import

from trainer import train
import pickle


class POSTHandler(tornado.web.RequestHandler):
    def post(self):
        for field_name, files in self.request.files.items():
            for info in files:
                filename, content_type = info["filename"], info["content_type"]
                body = info["body"].decode('UTF-8   ')

                file = open(filename, "w")
                file.write(body)
                
                models = train(filename)

                pickle.dump(models, open("models.nav", "wb"))



def make_app():
    return tornado.web.Application([(r"/post", POSTHandler)])


if __name__ == "__main__":
    # Tornado configures logging.
    options.parse_command_line()
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
















