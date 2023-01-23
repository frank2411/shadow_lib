from flask import current_app
from marshmallow import Schema, fields

from shadow_lib.api.resources import CustomerDetailResource, CustomerListResource

from shadow_lib.api.schemas import CustomerSchema
from shadow_lib.extensions import api_spec


class CustomerSchemaRich(Schema):
    message = fields.Str()
    customer = fields.Nested(CustomerSchema)


class CustomerSchemaMany(Schema):
    customers = fields.Nested(CustomerSchema(many=True))


api_spec.components.schema("CustomerSchema", schema=CustomerSchema)
api_spec.components.schema(
    "CustomerSchemaNoMessage", schema=CustomerSchemaRich(exclude=["message"])
)
api_spec.components.schema("CustomerSchemaRich", schema=CustomerSchemaRich)
api_spec.components.schema("CustomerSchemaMany", schema=CustomerSchemaMany)


api_spec.path(
    resource=CustomerListResource,
    # api=api,
    app=current_app,
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns a list of customers. Only for authenticated users.",
            description="Returns a list of customers. Only for authenticated users.",
            tags=["customers_list"],
            responses={
                "200": {
                    "description": "A JSON array of customer objects",
                    "content": {"application/json": {"schema": "CustomerSchemaMany"}},
                }
            },
        ),
        post=dict(
            security=[{"bearerAuth": []}],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "CustomerSchema",
                    }
                },
            },
            summary="Creates a customer",
            description="Creates a customer",
            tags=["customers_list"],
            responses={
                "201": {
                    "description": "Created",
                    "content": {"application/json": {"schema": "CustomerSchemaRich"}},
                },
                "422": {
                    "description": "List of errors occured in creation.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
    ),
)


# OrganizationDetailResource
api_spec.path(
    resource=CustomerDetailResource,
    # api=api,
    app=current_app,
    parameters=[
        {
            "name": "id",
            "in": "path",
            "required": True,
            "description": "Customer id on which perfom actions.",
            "schema": {"type": "string", "format": "uuid"},
        }
    ],
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns an customer by ID, if it exists",
            description="Returns an customer by ID, if it exists",
            tags=["customers_detail"],
            responses={
                "200": {
                    "description": "OK",
                    "content": {
                        "application/json": {"schema": "CustomerSchemaNoMessage"}
                    },
                },
                "404": {
                    "description": "customer not found.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        ),
        patch=dict(
            security=[{"bearerAuth": []}],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "CustomerSchema",
                    }
                },
            },
            summary="Updates an customer",
            description="Updates an customer",
            tags=["customers_detail"],
            responses={
                "200": {
                    "description": "customer updated",
                    "content": {"application/json": {"schema": "CustomerSchemaRich"}},
                },
                "422": {
                    "description": "List of errors occured in update.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
        delete=dict(
            security=[{"bearerAuth": []}],
            summary="Deletes an customer",
            description="Deletes an customer",
            tags=["customers_detail"],
            responses={
                "200": {
                    "description": "customer deleted",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "404": {
                    "description": "customer not found.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        ),
    ),
)
