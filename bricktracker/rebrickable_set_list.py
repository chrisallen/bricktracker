from typing import Self

from .rebrickable_set import RebrickableSet
from .record_list import BrickRecordList


# All the rebrickable sets from the database
class RebrickableSetList(BrickRecordList[RebrickableSet]):

    # Queries
    select_query: str = 'rebrickable/set/list'
    refresh_query: str = 'rebrickable/set/need_refresh'

    # All the sets
    def all(self, /) -> Self:
        # Load the sets from the database
        for record in self.select():
            rebrickable_set = RebrickableSet(record=record)

            self.records.append(rebrickable_set)

        return self

    # Sets needing refresh
    def need_refresh(self, /) -> Self:
        # Load the sets from the database
        for record in self.select(
            override_query=self.refresh_query
        ):
            rebrickable_set = RebrickableSet(record=record)

            self.records.append(rebrickable_set)

        return self
