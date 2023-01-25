import uuid

from flask import current_app, g, request
from flask_restful import Resource
from marshmallow import ValidationError

from shadow_lib.decorators import authenticate_user, check_bearer_token


from shadow_lib.custom_types import ErrorResponseType, SuccessResponseType
from shadow_lib.models import Order
from shadow_lib.api.schemas import OrderSchema


class OrderDetailResource(Resource):

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self, order_id: uuid.UUID) -> SuccessResponseType:
        schema = OrderSchema()
        order = Order.get_order(order_id, g.current_user)
        return {"order": schema.dump(order)}

    def patch(self, order_id: uuid.UUID) -> SuccessResponseType | ErrorResponseType:
        order = Order.get_order(order_id, g.current_user)
        schema = OrderSchema(
            partial=True,
            instance=order,
            exclude=["borrowed_books", "has_been_returned"],
        )

        try:
            order = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        order.save()
        return {"message": "order updated", "order": schema.dump(order)}

    def delete(self, order_id: uuid.UUID) -> SuccessResponseType:
        order = Order.get_order(order_id, g.current_user)

        # Reset related books quantity
        for br_book in order.borrowed_books:
            br_book.book.qty += br_book.qty
            br_book.save()

        order.delete()
        current_app.logger.info(f"order {order.id} deleted")
        return {"message": "order deleted"}


class OrderListResource(Resource):
    """Creation and get_all"""

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self) -> SuccessResponseType:
        schema = OrderSchema(many=True)
        orders = Order.get_orders(g.current_user)
        return {"orders": schema.dump(orders)}

    def post(self) -> SuccessResponseType | ErrorResponseType:
        try:
            schema = OrderSchema()
            order: Order = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        order.created_by_id = g.current_user.id
        order.save()

        current_app.logger.info(f"order {order.id} created")

        return {
            "message": "order created",
            "order": schema.dump(order),
        }, 201


class OrderCloseResource(Resource):

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def patch(self, order_id: uuid.UUID) -> SuccessResponseType | ErrorResponseType:
        order = Order.get_order(order_id, g.current_user)
        order.has_been_returned = True
        order.save()

        for br_book in order.borrowed_books:
            br_book.book.qty += br_book.qty
            br_book.save()

        schema = OrderSchema()
        return {"message": "order closed", "order": schema.dump(order)}
