from typing import Any, Self, TYPE_CHECKING

from flask import current_app

from .part import BrickPart
from .record_list import BrickRecordList
if TYPE_CHECKING:
    from .minifigure import BrickMinifigure
    from .set import BrickSet


# Lego set or minifig parts
class BrickPartList(BrickRecordList[BrickPart]):
    brickset: 'BrickSet | None'
    minifigure: 'BrickMinifigure | None'
    order: str

    # Queries
    all_query: str = 'part/list/all'
    last_query: str = 'part/list/last'
    minifigure_query: str = 'part/list/from_minifigure'
    missing_query: str = 'part/list/missing'
    select_query: str = 'part/list/from_set'

    def __init__(self, /):
        super().__init__()

        # Placeholders
        self.brickset = None
        self.minifigure = None

        # Store the order for this list
        self.order = current_app.config['PARTS_DEFAULT_ORDER']

    # Load all parts
    def all(self, /) -> Self:
        for record in self.select(
            override_query=self.all_query,
            order=self.order
        ):
            part = BrickPart(record=record)

            self.records.append(part)

        return self

    # Load parts from a brickset or minifigure
    def load(
        self,
        brickset: 'BrickSet',
        /,
        *,
        minifigure: 'BrickMinifigure | None' = None,
    ) -> Self:
        # Save the brickset and minifigure
        self.brickset = brickset
        self.minifigure = minifigure

        # Load the parts from the database
        for record in self.select(order=self.order):
            part = BrickPart(
                brickset=self.brickset,
                minifigure=minifigure,
                record=record,
            )

            if current_app.config['SKIP_SPARE_PARTS'] and part.fields.is_spare:
                continue

            self.records.append(part)

        return self

    # Load generic parts from a minifigure
    def from_minifigure(
        self,
        minifigure: 'BrickMinifigure',
        /,
    ) -> Self:
        # Save the  minifigure
        self.minifigure = minifigure

        # Load the parts from the database
        for record in self.select(
            override_query=self.minifigure_query,
            order=self.order
        ):
            part = BrickPart(
                minifigure=minifigure,
                record=record,
            )

            if current_app.config['SKIP_SPARE_PARTS'] and part.fields.is_spare:
                continue

            self.records.append(part)

        return self

    # Load missing parts
    def missing(self, /) -> Self:
        for record in self.select(
            override_query=self.missing_query,
            order=self.order
        ):
            part = BrickPart(record=record)

            self.records.append(part)

        return self

    # Return a dict with common SQL parameters for a parts list
    def sql_parameters(self, /) -> dict[str, Any]:
        parameters: dict[str, Any] = {}

        # Set id
        if self.brickset is not None:
            parameters['u_id'] = self.brickset.fields.u_id

        # Use the minifigure number if present,
        # otherwise use the set number
        if self.minifigure is not None:
            parameters['set_num'] = self.minifigure.fields.fig_num
        elif self.brickset is not None:
            parameters['set_num'] = self.brickset.fields.set_num

        return parameters
