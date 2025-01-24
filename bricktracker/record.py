from sqlite3 import Row
from typing import Any, ItemsView, Tuple

from .fields import BrickRecordFields
from .sql import BrickSQL


# SQLite record
class BrickRecord(object):
    select_query: str
    insert_query: str

    # Fields
    fields: BrickRecordFields

    def __init__(self, /):
        self.fields = BrickRecordFields()

    # Load from a record
    def ingest(self, record: Row | dict[str, Any], /) -> None:
        # Brutally ingest the record
        for key in record.keys():
            setattr(self.fields, key, record[key])

    # Insert into the database
    # If we do not commit immediately, we defer the execute() call
    def insert(
        self,
        /,
        *,
        commit=True,
        no_defer=False,
        override_query: str | None = None
    ) -> Tuple[int, str]:
        if override_query:
            query = override_query
        else:
            query = self.insert_query

        database = BrickSQL()
        rows, q = database.execute(
            query,
            parameters=self.sql_parameters(),
            defer=not commit and not no_defer,
        )

        if commit:
            database.commit()

        return rows, q

    # Shorthand to field items
    def items(self, /) -> ItemsView[str, Any]:
        return self.fields.__dict__.items()

    # Get from the database using the query
    def select(self, /, *, override_query: str | None = None) -> Row | None:
        if override_query:
            query = override_query
        else:
            query = self.select_query

        return BrickSQL().fetchone(
            query,
            parameters=self.sql_parameters()
        )

    # Generic SQL parameters from fields
    def sql_parameters(self, /) -> dict[str, Any]:
        parameters: dict[str, Any] = {}
        for name, value in self.items():
            parameters[name] = value

        return parameters
