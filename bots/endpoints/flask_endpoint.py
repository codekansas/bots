#!/usr/bin/env python
"""Flask endpoing for the bot.

To run this on a server, can use:

    gunicorn python -m bots.endpoints.flask_endpoint
"""

from typing import Type, Union

import flask
from bots.backends.base import BaseBackend
from bots.backends.interfaces.flask_interface import FlaskBackend
from bots.config import parse_config

app = flask.Flask(__name__)


def is_flask_backend(t: Type[BaseBackend], name: str) -> bool:
    return issubclass(t, FlaskBackend)


@app.route("/<backend_id>", methods=["GET"])
def backend(backend_id: str) -> Union[str, flask.Response]:
    backends = parse_config(should_instantiate=is_flask_backend)
    if backend_id not in backends:
        return flask.abort(404)
    backend_obj = backends[backend_id]
    if not isinstance(backend_obj, FlaskBackend):
        return flask.abort(404)
    return backend_obj.run_flask()


@app.route("/")
def index() -> flask.Response:
    return flask.abort(404)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
