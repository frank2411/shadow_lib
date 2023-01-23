# mypy: ignore-errors
import uuid

from marshmallow_sqlalchemy.fields import Related
from sqlalchemy.orm.exc import NoResultFound


class FixedRelated(Related):  # pragma: no cover

    default_error_messages = {
        "invalid": "Could not deserialize related value {value!r}; expected a dictionary with keys {keys!r}",
        "not_found": "Related Object doesn't exist in DB",
        "invalid_uuid": "Not a valid UUID.",
    }

    def _deserialize(self, value, *args, **kwargs):
        """Deserialize a serialized value to a model instance.
        If the parent schema is transient, create a new (transient) instance.
        Otherwise, attempt to find an existing instance in the database.
        :param value: The value to deserialize.
        """
        if not isinstance(value, dict):
            if len(self.related_keys) != 1:
                keys = [prop.key for prop in self.related_keys]
                raise self.make_error("invalid", value=value, keys=keys)
            value = {self.related_keys[0].key: value}
        if self.transient:
            return self.related_model(**value)

        if self.related_model.id.type.__str__() == "UUID":
            try:
                uuid.UUID(value["id"])
            except (ValueError, AttributeError, TypeError) as error:
                raise self.make_error("invalid_uuid") from error

        try:
            result = self._get_existing_instance(
                self.session.query(self.related_model), value
            )
        except NoResultFound:
            # The related-object DNE in the DB, but we still want to deserialize it
            # ...perhaps we want to add it to the DB later
            raise self.make_error("not_found")
        return result

    def _serialize(self, value, attr, obj):
        ret = {prop.key: getattr(value, prop.key, None) for prop in self.related_keys}

        # Little hack to prevent errors in uuid deserialization
        if isinstance(ret["id"], uuid.UUID):
            ret["id"] = str(ret["id"])

        return ret if len(ret) > 1 else list(ret.values())[0]
