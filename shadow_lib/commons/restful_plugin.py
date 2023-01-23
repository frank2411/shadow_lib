import re
from typing import Any

# Schema helpers
# Parameter helpers
# Response helpers
# Path helpers
# Operation helpers
import yaml
from apispec import BasePlugin, yaml_utils
from apispec.exceptions import APISpecError
from flask import Flask
from flask_restful import Resource

# from flask-restplus
RE_URL = re.compile(r"<(?:[^:<>]+:)?([^<>]+)>")


class RestFulResourcePlugin(BasePlugin):
    @staticmethod
    def flaskpath2openapi(path: str) -> Any:
        """Convert a Flask URL rule to an OpenAPI-compliant path.
        :param str path: Flask path template.
        """

        if "id" in path:
            return RE_URL.sub(r"{id}", path)

        return RE_URL.sub(r"{\1}", path)

    def parse_operations(self, resource: Resource, operations: dict) -> None:

        if self.has_path:
            return

        for method in resource.methods:

            if method.lower() in operations:
                continue

            docstring = getattr(resource, method.lower()).__doc__
            if docstring:
                try:
                    operation = yaml_utils.load_yaml_from_docstring(docstring)
                except yaml.YAMLError:
                    operation = None
                operations[method.lower()] = operation or dict()

    def path_helper(
        self,
        path: str,
        operations: dict,
        resource: Resource = None,
        api: Any = None,
        app: Flask = None,
        **kwargs: Any,
    ) -> str:
        """Path helper that parses docstrings for operations. Adds a
        ``func`` parameter to `apispec.APISpec.path`.
        """

        self.has_path = False
        if path:
            self.has_path = True
            return path

        if not getattr(resource, "endpoint", None):
            raise APISpecError("Flask-RESTful resource needed")

        for rule in app.url_map.iter_rules():  # type: ignore
            if rule.endpoint.endswith("." + resource.endpoint):  # type: ignore
                break
        else:
            raise APISpecError(f"Cannot find blueprint resource {resource.endpoint}")  # type: ignore

        return self.flaskpath2openapi(rule.rule)

    def operation_helper(
        self,
        path: str = None,
        resource: Resource = None,
        operations: dict = None,
        **kwargs: Any,
    ) -> None:

        if operations is None:
            return
        try:
            self.parse_operations(resource, operations)
        except Exception:
            raise
