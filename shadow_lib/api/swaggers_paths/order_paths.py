from flask import current_app
from marshmallow import Schema, fields

from shadow_lib.api.resources import OrderDetailResource, OrderListResource

from shadow_lib.api.schemas import OrderSchema
from shadow_lib.extensions import api_spec


class OrderSchemaRich(Schema):
    message = fields.Str()
    order = fields.Nested(OrderSchema)


class OrderSchemaMany(Schema):
    orders = fields.Nested(OrderSchema(many=True))


api_spec.components.schema("OrderSchema", schema=OrderSchema)
api_spec.components.schema(
    "OrderSchemaNoMessage", schema=OrderSchemaRich(exclude=["message"])
)
api_spec.components.schema("OrderSchemaRich", schema=OrderSchemaRich)
api_spec.components.schema("OrderSchemaMany", schema=OrderSchemaMany)


api_spec.path(
    resource=OrderListResource,
    # api=api,
    app=current_app,
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns a list of order. Only for authenticated users.",
            description="Returns a list of order. Only for authenticated users.",
            tags=["orders_list"],
            responses={
                "200": {
                    "description": "A JSON array of order objects",
                    "content": {"application/json": {"schema": "OrderSchemaMany"}},
                }
            },
        ),
        post=dict(
            security=[{"bearerAuth": []}],
            requestBody={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": "OrderSchema",
                    }
                },
            },
            summary="Creates an order",
            description="Creates an order",
            tags=["orders_list"],
            responses={
                "201": {
                    "description": "Created",
                    "content": {"application/json": {"schema": "OrderSchemaRich"}},
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
    resource=OrderDetailResource,
    # api=api,
    app=current_app,
    parameters=[
        {
            "name": "id",
            "in": "path",
            "required": True,
            "description": "Order id on which perfom actions.",
            "schema": {"type": "string", "format": "uuid"},
        }
    ],
    operations=dict(
        get=dict(
            security=[{"bearerAuth": []}],
            summary="Returns an order by ID, if it exists",
            description="Returns an order by ID, if it exists",
            tags=["orders_detail"],
            responses={
                "200": {
                    "description": "OK",
                    "content": {"application/json": {"schema": "OrderSchemaNoMessage"}},
                },
                "404": {
                    "description": "order not found.",
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
                        "schema": "OrderSchema",
                    }
                },
            },
            summary="Updates an Order",
            description="Updates an Order",
            tags=["orders_detail"],
            responses={
                "200": {
                    "description": "order updated",
                    "content": {"application/json": {"schema": "OrderSchemaRich"}},
                },
                "422": {
                    "description": "List of errors occured in update.",
                    "content": {"application/json": {"schema": "GeneralErrorSchema"}},
                },
            },
        ),
        delete=dict(
            security=[{"bearerAuth": []}],
            summary="Deletes an order",
            description="Deletes an order",
            tags=["orders_detail"],
            responses={
                "200": {
                    "description": "order deleted",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
                "404": {
                    "description": "order not found.",
                    "content": {"application/json": {"schema": "GeneralMessageSchema"}},
                },
            },
        ),
    ),
)
