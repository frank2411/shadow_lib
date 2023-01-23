import yaml
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from shadow_lib.commons import RestFulResourcePlugin


OPENAPI_SPEC = """
openapi: 3.0.2
info:
  description: shadow lib APIs
  title: Shadow lib
  version: 1.0.0
servers:
- url: http://localhost:{port}/
  description: Local server for testing
  variables:
    port:
      enum:
      - '5000'
      default: '5000'
"""

settings = yaml.safe_load(OPENAPI_SPEC)

api_spec = APISpec(
    title="Shadow lib",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[RestFulResourcePlugin(), MarshmallowPlugin()],
    **settings
)

# Declare default security schema
bearer_auth_scheme = {"type": "http", "scheme": "bearer", "bearerFormat": "Hash"}
api_spec.components.security_scheme("bearerAuth", bearer_auth_scheme)
