import logging
from typing import Any, Self

from .exceptions import DatabaseException, ErrorException
from .metadata import BrickMetadata
from .sql import BrickSQL

logger = logging.getLogger(__name__)

# Allowed custom field types. The type only drives the input widget and light
# validation; the value is always stored as TEXT.
CUSTOM_FIELD_TYPES = ('text', 'number', 'date')


# Lego set custom field metadata (a typed, admin-defined per-set value)
class BrickSetCustomField(BrickMetadata):
    kind: str = 'custom field'

    # Set value endpoint
    set_state_endpoint: str = 'set.update_custom_field'

    # Queries
    delete_query: str = 'set/metadata/custom_field/delete'
    insert_query: str = 'set/metadata/custom_field/insert'
    select_query: str = 'set/metadata/custom_field/select'
    update_field_query: str = 'set/metadata/custom_field/update/field'
    update_set_value_query: str = 'set/metadata/custom_field/update/value'
    values_query: str = 'set/metadata/custom_field/values'

    # SQL column name uses an underscore (kind has a space), so override the
    # default which would produce "custom-field_{id}".
    def as_column(self, /) -> str:
        return 'custom_field_{id}'.format(id=self.fields.id)

    # Distinct values already in use for this field, to populate its filter dropdown.
    def distinct_values(self, /) -> list[str]:
        rows = BrickSQL().fetchall(
            self.values_query,
            column=self.as_column(),
        )

        return [row['value'] for row in rows]

    # Grab data from a form (name + type)
    def from_form(self, form: dict[str, str], /) -> Self:
        super().from_form(form)

        field_type = form.get('type', 'text')

        if field_type not in CUSTOM_FIELD_TYPES:
            raise ErrorException(
                'Unknown custom field type: {type}'.format(type=field_type)
            )

        self.fields.type = field_type

        return self

    # Insert into database (carry the type along)
    def insert(self, /, **_) -> None:
        super().insert(
            type=self.fields.type
        )

    # Update the per-set value of this custom field. Unlike the base
    # update_set_value (which targets a fixed column), the column name is
    # dynamic, so it is injected into the query like update_set_state does.
    def update_value(
        self,
        brickset: Any,
        /,
        *,
        json: Any | None = None,
        value: Any | None = None,
    ) -> Any:
        if value is None and json is not None:
            value = json.get('value', '')

        if value == '':
            value = None

        parameters = self.sql_parameters()
        parameters['set_id'] = brickset.fields.id
        parameters['value'] = value

        rows, _ = BrickSQL().execute_and_commit(
            self.update_set_value_query,
            parameters=parameters,
            name=self.as_column(),
        )

        if rows != 1:
            raise DatabaseException(
                'Could not update the custom field value for set {set} ({id})'.format(  # noqa: E501
                    set=brickset.fields.set,
                    id=brickset.fields.id,
                )
            )

        logger.info(
            'Custom field "{name}" value changed to "{value}" for set {set} ({id})'.format(  # noqa: E501
                name=self.fields.name,
                value=value,
                set=brickset.fields.set,
                id=brickset.fields.id,
            )
        )

        return value
