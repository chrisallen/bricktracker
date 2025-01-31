from typing import Self

from flask import current_app

from .record_list import BrickRecordList
from .set_owner import BrickSetOwner
from .set_owner_list import BrickSetOwnerList
from .set_status import BrickSetStatus
from .set_status_list import BrickSetStatusList
from .set_tag import BrickSetTag
from .set_tag_list import BrickSetTagList
from .set import BrickSet


# All the sets from the database
class BrickSetList(BrickRecordList[BrickSet]):
    themes: list[str]
    order: str

    # Queries
    damaged_minifigure_query: str = 'set/list/damaged_minifigure'
    damaged_part_query: str = 'set/list/damaged_part'
    generic_query: str = 'set/list/generic'
    light_query: str = 'set/list/light'
    missing_minifigure_query: str = 'set/list/missing_minifigure'
    missing_part_query: str = 'set/list/missing_part'
    select_query: str = 'set/list/all'
    using_minifigure_query: str = 'set/list/using_minifigure'
    using_part_query: str = 'set/list/using_part'

    def __init__(self, /):
        super().__init__()

        # Placeholders
        self.themes = []

        # Store the order for this list
        self.order = current_app.config['SETS_DEFAULT_ORDER']

    # All the sets
    def all(self, /) -> Self:
        themes = set()

        # Load the sets from the database
        for record in self.select(
            order=self.order,
            owners=BrickSetOwnerList(BrickSetOwner).as_columns(),
            statuses=BrickSetStatusList(BrickSetStatus).as_columns(),
            tags=BrickSetTagList(BrickSetTag).as_columns(),
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)
            themes.add(brickset.theme.name)

        # Convert the set into a list and sort it
        self.themes = list(themes)
        self.themes.sort()

        return self

    # Sets with a minifigure part damaged
    def damaged_minifigure(self, figure: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.figure = figure

        # Load the sets from the database
        for record in self.select(
            override_query=self.damaged_minifigure_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # Sets with a part damaged
    def damaged_part(self, part: str, color: int, /) -> Self:
        # Save the parameters to the fields
        self.fields.part = part
        self.fields.color = color

        # Load the sets from the database
        for record in self.select(
            override_query=self.damaged_part_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # A generic list of the different sets
    def generic(self, /) -> Self:
        for record in self.select(
            override_query=self.generic_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # Last added sets
    def last(self, /, *, limit: int = 6) -> Self:
        # Randomize
        if current_app.config['RANDOM']:
            order = 'RANDOM()'
        else:
            order = '"bricktracker_sets"."rowid" DESC'

        for record in self.select(
            order=order,
            limit=limit,
            owners=BrickSetOwnerList(BrickSetOwner).as_columns(),
            statuses=BrickSetStatusList(BrickSetStatus).as_columns(),
            tags=BrickSetTagList(BrickSetTag).as_columns(),
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # Sets missing a minifigure part
    def missing_minifigure(self, figure: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.figure = figure

        # Load the sets from the database
        for record in self.select(
            override_query=self.missing_minifigure_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # Sets missing a part
    def missing_part(self, part: str, color: int, /) -> Self:
        # Save the parameters to the fields
        self.fields.part = part
        self.fields.color = color

        # Load the sets from the database
        for record in self.select(
            override_query=self.missing_part_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # Sets using a minifigure
    def using_minifigure(self, figure: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.figure = figure

        # Load the sets from the database
        for record in self.select(
            override_query=self.using_minifigure_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # Sets using a part
    def using_part(self, part: str, color: int, /) -> Self:
        # Save the parameters to the fields
        self.fields.part = part
        self.fields.color = color

        # Load the sets from the database
        for record in self.select(
            override_query=self.using_part_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self
