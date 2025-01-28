from sqlite3 import Row
from typing import Any, Self
from uuid import uuid4

from flask import url_for

from .exceptions import DatabaseException, ErrorException, NotFoundException
from .record import BrickRecord
from .sql import BrickSQL


# Lego set checkbox
class BrickSetCheckbox(BrickRecord):
    # Queries
    select_query: str = 'checkbox/select'

    def __init__(
        self,
        /,
        *,
        record: Row | dict[str, Any] | None = None,
    ):
        super().__init__()

        # Ingest the record if it has one
        if record is not None:
            self.ingest(record)

    # SQL column name
    def as_column(self) -> str:
        return 'status_{id}'.format(id=self.fields.id)

    # HTML dataset name
    def as_dataset(self) -> str:
        return '{id}'.format(
            id=self.as_column().replace('_', '-')
        )

    # Delete from database
    def delete(self) -> None:
        BrickSQL().executescript(
            'checkbox/delete',
            id=self.fields.id,
        )

    # Grab data from a form
    def from_form(self, form: dict[str, str]) -> Self:
        name = form.get('name', None)
        grid = form.get('grid', None)

        if name is None or name == '':
            raise ErrorException('Checkbox name cannot be empty')

        # Security: eh.
        # Prevent self-ownage with accidental quote escape
        self.fields.name = name
        self.fields.safe_name = self.fields.name.replace("'", "''")
        self.fields.displayed_on_grid = grid == 'on'

        return self

    # Insert into database
    def insert(self, **_) -> None:
        # Generate an ID for the checkbox (with underscores to make it
        # column name friendly)
        self.fields.id = str(uuid4()).replace('-', '_')

        BrickSQL().executescript(
            'checkbox/add',
            id=self.fields.id,
            name=self.fields.safe_name,
            displayed_on_grid=self.fields.displayed_on_grid
        )

    # Rename the checkbox
    def rename(self, /) -> None:
        # Update the name
        rows, _ = BrickSQL().execute_and_commit(
            'checkbox/update/name',
            parameters=self.sql_parameters(),
        )

        if rows != 1:
            raise DatabaseException('Could not update the name for checkbox {name} ({id})'.format(  # noqa: E501
                name=self.fields.name,
                id=self.fields.id,
            ))

    # URL to change the status
    def status_url(self, id: str) -> str:
        return url_for(
            'set.update_status',
            id=id,
            checkbox_id=self.fields.id
        )

    # Select a specific checkbox (with an id)
    def select_specific(self, id: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.id = id

        # Load from database
        if not self.select():
            raise NotFoundException(
                'Checkbox with ID {id} was not found in the database'.format(
                    id=self.fields.id,
                ),
            )

        return self

    # Update a status
    def update_status(
        self,
        name: str,
        status: bool,
        /
    ) -> None:
        if not hasattr(self.fields, name) or name in ['id', 'name']:
            raise NotFoundException('{name} is not a field of a checkbox'.format(  # noqa: E501
                name=name
            ))

        parameters = self.sql_parameters()
        parameters['status'] = status

        # Update the status
        rows, _ = BrickSQL().execute_and_commit(
            'checkbox/update/status',
            parameters=parameters,
            name=name,
        )

        if rows != 1:
            raise DatabaseException('Could not update the status "{status}" for checkbox {name} ({id})'.format(  # noqa: E501
                status=name,
                name=self.fields.name,
                id=self.fields.id,
            ))
