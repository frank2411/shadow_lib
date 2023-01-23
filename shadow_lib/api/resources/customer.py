import uuid

from flask import current_app, g, request
from flask_restful import Resource
from marshmallow import ValidationError

from shadow_lib.decorators import authenticate_user, check_bearer_token


from shadow_lib.custom_types import ErrorResponseType, SuccessResponseType
from shadow_lib.models import Customer
from shadow_lib.api.schemas import CustomerSchema


class CustomerDetailResource(Resource):

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self, customer_id: uuid.UUID) -> SuccessResponseType:
        schema = CustomerSchema()
        customer = Customer.get_customer(customer_id, g.current_user)
        return {"customer": schema.dump(customer)}

    def patch(self, customer_id: uuid.UUID) -> SuccessResponseType | ErrorResponseType:
        customer = Customer.get_customer(customer_id, g.current_user)
        schema = CustomerSchema(partial=True, instance=customer)

        try:
            customer = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        customer.save()
        return {"message": "customer updated", "customer": schema.dump(customer)}

    def delete(self, customer_id: uuid.UUID) -> SuccessResponseType:
        customer = Customer.get_customer(customer_id, g.current_user)
        customer.delete()
        current_app.logger.info(f"customer {customer.id} deleted")
        return {"message": "customer deleted"}


class CustomerListResource(Resource):
    """Creation and get_all"""

    method_decorators = [
        authenticate_user,
        check_bearer_token,
    ]

    def get(self) -> SuccessResponseType:
        schema = CustomerSchema(many=True)
        customers = Customer.get_customers(g.current_user)
        return {"customers": schema.dump(customers)}

    def post(self) -> SuccessResponseType | ErrorResponseType:
        try:
            schema = CustomerSchema()
            customer: Customer = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        customer.created_by_id = g.current_user.id
        customer.save()

        current_app.logger.info(f"customer {customer.id} created")

        return {
            "message": "customer created",
            "customer": schema.dump(customer),
        }, 201
