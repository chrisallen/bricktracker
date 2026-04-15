import logging
from sqlite3 import Row
from typing import Any, Self, TYPE_CHECKING
from uuid import uuid4

from flask import url_for

from .exceptions import DatabaseException, ErrorException, NotFoundException
from .record import BrickRecord
from .sql import BrickSQL
if TYPE_CHECKING:
    from .individual_minifigure import IndividualMinifigure
    from .individual_part import IndividualPart
    from .set import BrickSet

logger = logging.getLogger(__name__)


# Lego set metadata (customizable list of entries that can be checked)
class BrickMetadata(BrickRecord):
    kind: str

    # Set state endpoint
    set_state_endpoint: str

    # Queries
    delete_query: str
    insert_query: str
    select_query: str
    update_field_query: str
    update_set_state_query: str
    update_set_value_query: str

    def __init__(
        self,
        /,
        *,
        record: Row | dict[str, Any] | None = None,
    ):
        super().__init__()

        # Defined an empty ID
        self.fields.id = None

        # Ingest the record if it has one
        if record is not None:
            self.ingest(record)

    # SQL column name
    def as_column(self, /) -> str:
        return '{kind}_{id}'.format(
            id=self.fields.id,
            kind=self.kind.lower().replace(' ', '-')
        )

    # HTML dataset name
    def as_dataset(self, /) -> str:
        return self.as_column().replace('_', '-')

    # Delete from database
    def delete(self, /) -> None:
        BrickSQL().executescript(
            self.delete_query,
            id=self.fields.id,
        )

    # Grab data from a form
    def from_form(self, form: dict[str, str], /) -> Self:
        name = form.get('name', None)

        if name is None or name == '':
            raise ErrorException('Status name cannot be empty')

        self.fields.name = name

        return self

    # Insert into database
    def insert(self, /, **context) -> None:
        self.safe()

        # Generate an ID for the metadata (with underscores to make it
        # column name friendly)
        self.fields.id = str(uuid4()).replace('-', '_')

        BrickSQL().executescript(
            self.insert_query,
            id=self.fields.id,
            name=self.fields.safe_name,
            **context
        )

    # Rename the entry
    def rename(self, /) -> None:
        self.update_field('name', value=self.fields.name)

    # Make the name "safe"
    # Security: eh.
    def safe(self, /) -> None:
        # Prevent self-ownage with accidental quote escape
        self.fields.safe_name = self.fields.name.replace("'", "''")

    # URL to change the selected state of this metadata item for a set
    def url_for_set_state(self, id: str, /) -> str:
        return url_for(
            self.set_state_endpoint,
            id=id,
            metadata_id=self.fields.id
        )

    # URL to change the selected state of this metadata item for an individual part
    def url_for_individual_part_state(self, part_id: str, /) -> str:
        # Replace 'set' with 'individual_part' in the endpoint name
        endpoint = self.set_state_endpoint.replace('set.', 'individual_part.')
        return url_for(
            endpoint,
            id=part_id,
            metadata_id=self.fields.id
        )

    # URL to change the selected state of this metadata item for an individual minifigure
    def url_for_individual_minifigure_state(self, minifigure_id: str, /) -> str:
        # Replace 'set' with 'individual_minifigure' in the endpoint name
        endpoint = self.set_state_endpoint.replace('set.', 'individual_minifigure.')
        return url_for(
            endpoint,
            id=minifigure_id,
            metadata_id=self.fields.id
        )

    # Select a specific metadata (with an id)
    def select_specific(self, id: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.id = id

        # Load from database
        if not self.select():
            raise NotFoundException(
                '{kind} with ID {id} was not found in the database'.format(
                    kind=self.kind.capitalize(),
                    id=self.fields.id,
                ),
            )

        return self

    # Update a field
    def update_field(
        self,
        field: str,
        /,
        *,
        json: Any | None = None,
        value: Any | None = None
    ) -> Any:
        if value is None and json is not None:
            value = json.get('value', None)

        if value is None:
            raise ErrorException('"{field}" of a {kind} cannot be set to an empty value'.format(  # noqa: E501
                field=field,
                kind=self.kind
            ))

        if field == 'id' or not hasattr(self.fields, field):
            raise NotFoundException('"{field}" is not a field of a {kind}'.format(  # noqa: E501
                kind=self.kind,
                field=field
            ))

        parameters = self.sql_parameters()
        parameters['value'] = value

        # Update the status
        rows, _ = BrickSQL().execute_and_commit(
            self.update_field_query,
            parameters=parameters,
            field=field,
        )

        if rows != 1:
            raise DatabaseException('Could not update the field "{field}" for {kind} "{name}" ({id})'.format(  # noqa: E501
                field=field,
                kind=self.kind,
                name=self.fields.name,
                id=self.fields.id,
            ))

        # Info
        logger.info('{kind} "{name}" ({id}): field "{field}" changed to "{value}"'.format(  # noqa: E501
            kind=self.kind.capitalize(),
            name=self.fields.name,
            id=self.fields.id,
            field=field,
            value=value,
        ))

        return value

    # Update the selected state of this metadata item for a set
    def update_set_state(
        self,
        brickset: 'BrickSet',
        /,
        *,
        json: Any | None = None,
        state: Any | None = None,
        commit: bool = True
    ) -> Any:
        if state is None and json is not None:
            state = json.get('value', False)

        parameters = self.sql_parameters()
        parameters['set_id'] = brickset.fields.id
        parameters['state'] = state

        if commit:
            rows, _ = BrickSQL().execute_and_commit(
                self.update_set_state_query,
                parameters=parameters,
                name=self.as_column(),
            )
        else:
            rows, _ = BrickSQL().execute(
                self.update_set_state_query,
                parameters=parameters,
                defer=True,
                name=self.as_column(),
            )

        # When deferred, rows will be -1, so skip the check
        if commit and rows != 1:
            raise DatabaseException('Could not update the {kind} state for set {set} ({id})'.format(
                kind=self.kind,
                set=brickset.fields.set,
                id=brickset.fields.id,
            ))

        # Info
        logger.info('{kind} "{name}" state changed to "{state}" for set {set} ({id})'.format(  # noqa: E501
            kind=self.kind,
            name=self.fields.name,
            state=state,
            set=brickset.fields.set,
            id=brickset.fields.id,
        ))

        return state

    # Update the selected value of this metadata item for a set
    def update_set_value(
        self,
        brickset: 'BrickSet',
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
        )

        # Update the status
        if value is None and not hasattr(self.fields, 'name'):
            self.fields.name = 'None'

        if rows != 1:
            raise DatabaseException('Could not update the {kind} value for set {set} ({id})'.format(  # noqa: E501
                kind=self.kind,
                set=brickset.fields.set,
                id=brickset.fields.id,
            ))

        # Info
        logger.info('{kind} value changed to "{name}" ({value}) for set {set} ({id})'.format(  # noqa: E501
            kind=self.kind,
            name=self.fields.name,
            value=value,
            set=brickset.fields.set,
            id=brickset.fields.id,
        ))

        return value

    # Update the selected state of this metadata item for an individual part
    def update_individual_part_state(
        self,
        individual_part: 'IndividualPart',
        /,
        *,
        json: Any | None = None,
        state: Any | None = None,
        commit: bool = True
    ) -> Any:
        if state is None and json is not None:
            state = json.get('value', False)

        parameters = self.sql_parameters()
        parameters['set_id'] = individual_part.fields.id  # set_id parameter accepts any entity id
        parameters['state'] = state

        # Use the same set query (bricktracker_set_owners/tags/statuses tables accept any entity id)
        query_name = self.update_set_state_query

        if commit:
            rows, _ = BrickSQL().execute_and_commit(
                query_name,
                parameters=parameters,
                name=self.as_column(),
            )
        else:
            rows, _ = BrickSQL().execute(
                query_name,
                parameters=parameters,
                defer=True,
                name=self.as_column(),
            )

        # When deferred, rows will be -1, so skip the check
        if commit and rows != 1:
            raise DatabaseException('Could not update the {kind} state for individual part {part_id}'.format(
                kind=self.kind,
                part_id=individual_part.fields.id,
            ))

        # Info
        logger.info('{kind} "{name}" state changed to "{state}" for individual part {part_id}'.format(
            kind=self.kind,
            name=self.fields.name,
            state=state,
            part_id=individual_part.fields.id,
        ))

        return state

    # Update the selected state of this metadata item for an individual minifigure
    def update_individual_minifigure_state(
        self,
        individual_minifigure: 'IndividualMinifigure',
        /,
        *,
        json: Any | None = None,
        state: Any | None = None,
        commit: bool = True
    ) -> Any:
        if state is None and json is not None:
            state = json.get('value', False)

        parameters = self.sql_parameters()
        parameters['set_id'] = individual_minifigure.fields.id  # set_id parameter accepts any entity id
        parameters['state'] = state

        # Use the same set query (bricktracker_set_owners/tags/statuses tables accept any entity id)
        query_name = self.update_set_state_query

        if commit:
            rows, _ = BrickSQL().execute_and_commit(
                query_name,
                parameters=parameters,
                name=self.as_column(),
            )
        else:
            rows, _ = BrickSQL().execute(
                query_name,
                parameters=parameters,
                defer=True,
                name=self.as_column(),
            )

        # When deferred, rows will be -1, so skip the check
        if commit and rows != 1:
            raise DatabaseException('Could not update the {kind} state for individual minifigure {minifigure_id}'.format(
                kind=self.kind,
                minifigure_id=individual_minifigure.fields.id,
            ))

        # Info
        logger.info('{kind} "{name}" state changed to "{state}" for individual minifigure {minifigure_id}'.format(
            kind=self.kind,
            name=self.fields.name,
            state=state,
            minifigure_id=individual_minifigure.fields.id,
        ))

        return state

    # Update the selected state of this metadata item for an individual part lot
    def update_individual_part_lot_state(
        self,
        individual_part_lot: 'IndividualPartLot',
        /,
        *,
        json: Any | None = None,
        state: Any | None = None,
        commit: bool = True
    ) -> Any:
        if state is None and json is not None:
            state = json.get('value', False)

        parameters = self.sql_parameters()
        parameters['set_id'] = individual_part_lot.fields.id  # set_id parameter accepts any entity id
        parameters['state'] = state

        # Use the same set query (bricktracker_set_owners/tags tables accept any entity id)
        query_name = self.update_set_state_query

        if commit:
            rows, _ = BrickSQL().execute_and_commit(
                query_name,
                parameters=parameters,
                name=self.as_column(),
            )
        else:
            rows, _ = BrickSQL().execute(
                query_name,
                parameters=parameters,
                defer=True,
                name=self.as_column(),
            )

        # When deferred, rows will be -1, so skip the check
        if commit and rows != 1:
            raise DatabaseException('Could not update the {kind} state for individual part lot {lot_id}'.format(
                kind=self.kind,
                lot_id=individual_part_lot.fields.id,
            ))

        # Info
        logger.info('{kind} "{name}" state changed to "{state}" for individual part lot {lot_id}'.format(
            kind=self.kind,
            name=self.fields.name,
            state=state,
            lot_id=individual_part_lot.fields.id,
        ))

        return state
