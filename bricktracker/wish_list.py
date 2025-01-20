from typing import Self

from flask import current_app

from bricktracker.exceptions import NotFoundException

from .rebrickable_set import RebrickableSet
from .record_list import BrickRecordList
from .wish import BrickWish


# All the wished sets from the database
class BrickWishList(BrickRecordList[BrickWish]):
    # Queries
    select_query: str = 'wish/list/all'

    # All the wished sets
    def all(self, /) -> Self:
        # Load the wished sets from the database
        for record in self.select(
            order=current_app.config['WISHES_DEFAULT_ORDER']
        ):
            brickwish = BrickWish(record=record)

            self.records.append(brickwish)

        return self

    # Add a set to the wishlist
    @staticmethod
    def add(set_num: str, /) -> None:
        # Check if it already exists
        try:
            set_num = RebrickableSet.parse_number(set_num)
            BrickWish().select_specific(set_num)
        except NotFoundException:
            RebrickableSet.wish(set_num)
