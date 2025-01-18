from typing import Any, Self, TYPE_CHECKING

from flask import current_app

from .minifigure import BrickMinifigure
from .record_list import BrickRecordList
if TYPE_CHECKING:
    from .set import BrickSet


# Lego minifigures
class BrickMinifigureList(BrickRecordList[BrickMinifigure]):
    brickset: 'BrickSet | None'
    order: str

    # Queries
    all_query: str = 'minifigure/list/all'
    last_query: str = 'minifigure/list/last'
    select_query: str = 'minifigure/list/from_set'
    using_part_query: str = 'minifigure/list/using_part'
    missing_part_query: str = 'minifigure/list/missing_part'

    def __init__(self, /):
        super().__init__()

        # Placeholders
        self.brickset = None

        # Store the order for this list
        self.order = current_app.config['MINIFIGURES_DEFAULT_ORDER'].value

    # Load all minifigures
    def all(self, /) -> Self:
        for record in self.select(
            override_query=self.all_query,
            order=self.order
        ):
            minifigure = BrickMinifigure(record=record)

            self.records.append(minifigure)

        return self

    # Last added minifigure
    def last(self, /, limit: int = 6) -> Self:
        # Randomize
        if current_app.config['RANDOM'].value:
            order = 'RANDOM()'
        else:
            order = 'minifigures.rowid DESC'

        for record in self.select(
            override_query=self.last_query,
            order=order,
            limit=limit
        ):
            minifigure = BrickMinifigure(record=record)

            self.records.append(minifigure)

        return self

    # Load minifigures from a brickset
    def load(self, brickset: 'BrickSet', /) -> Self:
        # Save the brickset
        self.brickset = brickset

        # Load the minifigures from the database
        for record in self.select(order=self.order):
            minifigure = BrickMinifigure(brickset=self.brickset, record=record)

            self.records.append(minifigure)

        return self

    # Return a dict with common SQL parameters for a minifigures list
    def sql_parameters(self, /) -> dict[str, Any]:
        parameters: dict[str, Any] = super().sql_parameters()

        if self.brickset is not None:
            parameters['u_id'] = self.brickset.fields.u_id
            parameters['set_num'] = self.brickset.fields.set_num

        return parameters

    # Minifigures missing a part
    def missing_part(
        self,
        part_num: str,
        color_id: int,
        /,
        element_id: int | None = None,
    ) -> Self:
        # Save the parameters to the fields
        self.fields.part_num = part_num
        self.fields.color_id = color_id
        self.fields.element_id = element_id

        # Load the minifigures from the database
        for record in self.select(
            override_query=self.missing_part_query,
            order=self.order
        ):
            minifigure = BrickMinifigure(record=record)

            self.records.append(minifigure)

        return self

    # Minifigure using a part
    def using_part(
        self,
        part_num: str,
        color_id: int,
        /,
        element_id: int | None = None,
    ) -> Self:
        # Save the parameters to the fields
        self.fields.part_num = part_num
        self.fields.color_id = color_id
        self.fields.element_id = element_id

        # Load the minifigures from the database
        for record in self.select(
            override_query=self.using_part_query,
            order=self.order
        ):
            minifigure = BrickMinifigure(record=record)

            self.records.append(minifigure)

        return self
