from sqlite3 import Row
from typing import Any, ItemsView

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
    def insert(self, /, commit=True) -> None:
        database = BrickSQL()
        rows, q = database.execute(
            self.insert_query,
            parameters=self.sql_parameters(),
            defer=not commit,
        )

        if commit:
            database.commit()

    # Shorthand to field items
    def items(self, /) -> ItemsView[str, Any]:
        return self.fields.__dict__.items()

    # Get from the database using the query
    def select(self, /, override_query: str | None = None) -> Row | None:
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
