from typing import Self

from flask import url_for

from .exceptions import NotFoundException
from .rebrickable_set import RebrickableSet
from .sql import BrickSQL


# Lego brick wished set
class BrickWish(RebrickableSet):
    # Flags
    resolve_instructions: bool = False

    # Queries
    select_query: str = 'wish/select'
    insert_query: str = 'wish/insert'

    # Delete a wished set
    def delete(self, /) -> None:
        BrickSQL().execute_and_commit(
            'wish/delete/wish',
            parameters=self.sql_parameters()
        )

    # Select a specific part (with a set and an id)
    def select_specific(self, set: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.set = set

        # Load from database
        if not self.select():
            raise NotFoundException(
                'Wish for set {set} was not found in the database'.format(  # noqa: E501
                    set=self.fields.set,
                ),
            )

        return self

    # Deletion url
    def url_for_delete(self, /) -> str:
        return url_for('wish.delete', number=self.fields.set)
