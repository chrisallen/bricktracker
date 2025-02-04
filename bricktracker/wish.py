from typing import Self

from flask import url_for

from .exceptions import NotFoundException
from .rebrickable_set import RebrickableSet
from .sql import BrickSQL
from .wish_owner_list import BrickWishOwnerList


# Lego brick wished set
class BrickWish(RebrickableSet):
    # Flags
    resolve_instructions: bool = False

    # Queries
    select_query: str = 'wish/select'
    insert_query: str = 'wish/insert'

    # Delete a wish
    def delete(self, /) -> None:
        BrickSQL().executescript(
            'wish/delete/wish',
            set=self.fields.set
        )

    # Select a specific part (with a set and an id)
    def select_specific(self, set: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.set = set

        # Load from database
        if not self.select(owners=BrickWishOwnerList.as_columns()):
            raise NotFoundException(
                'Wish for set {set} was not found in the database'.format(  # noqa: E501
                    set=self.fields.set,
                ),
            )

        return self

    # Self url
    def url(self, /) -> str:
        return url_for('wish.details', set=self.fields.set)

    # Deletion url
    def url_for_delete(self, /) -> str:
        return url_for('wish.delete', set=self.fields.set)

    # Actual deletion url
    def url_for_do_delete(self, /) -> str:
        return url_for('wish.do_delete', set=self.fields.set)
