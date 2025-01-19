from sqlite3 import Row
from typing import Any, Self

from flask import url_for

from .exceptions import NotFoundException
from .set import BrickSet
from .sql import BrickSQL


# Lego brick wished set
class BrickWish(BrickSet):
    # Queries
    select_query: str = 'wish/select'
    insert_query: str = 'wish/insert'

    def __init__(
        self,
        /,
        record: Row | dict[str, Any] | None = None,
    ):
        # Don't init BrickSet, init the parent of BrickSet directly
        super(BrickSet, self).__init__()

        # Placeholders
        self.theme_name = ''

        # Ingest the record if it has one
        if record is not None:
            self.ingest(record)

            # Resolve the theme
            self.resolve_theme()

    # Delete a wished set
    def delete(self, /) -> None:
        BrickSQL().execute_and_commit(
            'wish/delete/wish',
            parameters=self.sql_parameters()
        )

    # Select a specific part (with a set and an id)
    def select_specific(self, set_num: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.set_num = set_num

        # Load from database
        record = self.select()

        if record is None:
            raise NotFoundException(
                'Wish with number {number} was not found in the database'.format(  # noqa: E501
                    number=self.fields.set_num,
                ),
            )

        # Ingest the record
        self.ingest(record)

        # Resolve the theme
        self.resolve_theme()

        return self

    # Deletion url
    def url_for_delete(self, /) -> str:
        return url_for('wish.delete', number=self.fields.set_num)

    # Normalize from Rebrickable
    @staticmethod
    def from_rebrickable(data: dict[str, Any], /, **_) -> dict[str, Any]:
        return {
            'set_num': data['set_num'],
            'name': data['name'],
            'year': data['year'],
            'theme_id': data['theme_id'],
            'num_parts': data['num_parts'],
            'set_img_url': data['set_img_url'],
            'set_url': data['set_url'],
            'last_modified_dt': data['last_modified_dt'],
        }
