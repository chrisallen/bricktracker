from typing import Any, Self, Union

from flask import current_app

from .record_list import BrickRecordList
from .set_owner import BrickSetOwner
from .set_owner_list import BrickSetOwnerList
from .set_purchase_location import BrickSetPurchaseLocation
from .set_purchase_location_list import BrickSetPurchaseLocationList
from .set_status_list import BrickSetStatusList
from .set_storage import BrickSetStorage
from .set_storage_list import BrickSetStorageList
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
    using_storage_query: str = 'set/list/using_storage'

    def __init__(self, /):
        super().__init__()

        # Placeholders
        self.themes = []

        # Store the order for this list
        self.order = current_app.config['SETS_DEFAULT_ORDER']

    # All the sets
    def all(self, /) -> Self:
        # Load the sets from the database
        self.list(do_theme=True)

        return self

    # Sets with a minifigure part damaged
    def damaged_minifigure(self, figure: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.figure = figure

        # Load the sets from the database
        self.list(override_query=self.damaged_minifigure_query)

        return self

    # Sets with a part damaged
    def damaged_part(self, part: str, color: int, /) -> Self:
        # Save the parameters to the fields
        self.fields.part = part
        self.fields.color = color

        # Load the sets from the database
        self.list(override_query=self.damaged_part_query)

        return self

    # Last added sets
    def last(self, /, *, limit: int = 6) -> Self:
        # Randomize
        if current_app.config['RANDOM']:
            order = 'RANDOM()'
        else:
            order = '"bricktracker_sets"."rowid" DESC'

        self.list(order=order, limit=limit)

        return self

    # Base set list
    def list(
        self,
        /,
        *,
        override_query: str | None = None,
        order: str | None = None,
        limit: int | None = None,
        do_theme: bool = False,
        **context: Any,
    ) -> None:
        themes = set()

        if order is None:
            order = self.order

        # Load the sets from the database
        for record in super().select(
            override_query=override_query,
            order=order,
            limit=limit,
            owners=BrickSetOwnerList.as_columns(),
            statuses=BrickSetStatusList.as_columns(),
            tags=BrickSetTagList.as_columns(),
        ):
            brickset = BrickSet(record=record)

            self.records.append(brickset)
            if do_theme:
                themes.add(brickset.theme.name)

        # Convert the set into a list and sort it
        if do_theme:
            self.themes = list(themes)
            self.themes.sort()

    # Sets missing a minifigure part
    def missing_minifigure(self, figure: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.figure = figure

        # Load the sets from the database
        self.list(override_query=self.missing_minifigure_query)

        return self

    # Sets missing a part
    def missing_part(self, part: str, color: int, /) -> Self:
        # Save the parameters to the fields
        self.fields.part = part
        self.fields.color = color

        # Load the sets from the database
        self.list(override_query=self.missing_part_query)

        return self

    # Sets using a minifigure
    def using_minifigure(self, figure: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.figure = figure

        # Load the sets from the database
        self.list(override_query=self.using_minifigure_query)

        return self

    # Sets using a part
    def using_part(self, part: str, color: int, /) -> Self:
        # Save the parameters to the fields
        self.fields.part = part
        self.fields.color = color

        # Load the sets from the database
        self.list(override_query=self.using_part_query)

        return self

    # Sets using a storage
    def using_storage(self, storage: BrickSetStorage, /) -> Self:
        # Save the parameters to the fields
        self.fields.storage = storage.fields.id

        # Load the sets from the database
        self.list(override_query=self.using_storage_query)

        return self


# Helper to build the metadata lists
def set_metadata_lists(
    as_class: bool = False
) -> dict[
    str,
    Union[
        list[BrickSetOwner],
        list[BrickSetPurchaseLocation],
        BrickSetPurchaseLocation,
        list[BrickSetStorage],
        BrickSetStorageList,
        list[BrickSetTag]
    ]
]:
    return {
        'brickset_owners': BrickSetOwnerList.list(),
        'brickset_purchase_locations': BrickSetPurchaseLocationList.list(as_class=as_class),  # noqa: E501
        'brickset_storages': BrickSetStorageList.list(as_class=as_class),
        'brickset_tags': BrickSetTagList.list(),
    }
