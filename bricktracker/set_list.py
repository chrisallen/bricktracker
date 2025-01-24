from typing import Self

from flask import current_app

from .record_list import BrickRecordList
from .set_checkbox_list import BrickSetCheckboxList
from .set import BrickSet


# All the sets from the database
class BrickSetList(BrickRecordList[BrickSet]):
    themes: list[str]
    order: str

    # Queries
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
            statuses=BrickSetCheckboxList().as_columns()
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)
            themes.add(brickset.theme.name)

        # Convert the set into a list and sort it
        self.themes = list(themes)
        self.themes.sort()

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
            statuses=BrickSetCheckboxList().as_columns()
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # Sets missing a minifigure
    def missing_minifigure(
        self,
        fig_num: str,
        /
    ) -> Self:
        # Save the parameters to the fields
        self.fields.fig_num = fig_num

        # Load the sets from the database
        for record in self.select(
            override_query=self.missing_minifigure_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # Sets missing a part
    def missing_part(
        self,
        part_num: str,
        color_id: int,
        /,
        *,
        element_id: int | None = None,
    ) -> Self:
        # Save the parameters to the fields
        self.fields.part_num = part_num
        self.fields.color_id = color_id
        self.fields.element_id = element_id

        # Load the sets from the database
        for record in self.select(
            override_query=self.missing_part_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # Sets using a minifigure
    def using_minifigure(
        self,
        fig_num: str,
        /
    ) -> Self:
        # Save the parameters to the fields
        self.fields.fig_num = fig_num

        # Load the sets from the database
        for record in self.select(
            override_query=self.using_minifigure_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self

    # Sets using a part
    def using_part(
        self,
        part_num: str,
        color_id: int,
        /,
        *,
        element_id: int | None = None,
    ) -> Self:
        # Save the parameters to the fields
        self.fields.part_num = part_num
        self.fields.color_id = color_id
        self.fields.element_id = element_id

        # Load the sets from the database
        for record in self.select(
            override_query=self.using_part_query,
            order=self.order
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)

        return self
