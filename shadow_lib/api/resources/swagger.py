from flask import Response, make_response, render_template
from flask_restful import Resource


class SwaggerView(Resource):  # pragma: no cover
    def get(self) -> Response:
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("swagger/index.html"), 200, headers)


class SwaggerJsonView(Resource):  # pragma: no cover
    def get(self) -> Response:
        from shadow_lib.api.swaggers_paths import (
            api_spec,
        )  # Avoids ugly circular imports

        return api_spec.to_dict()
