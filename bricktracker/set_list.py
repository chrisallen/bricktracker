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
from .theme_list import BrickThemeList
from .instructions_list import BrickInstructionsList


# All the sets from the database
class BrickSetList(BrickRecordList[BrickSet]):
    themes: list[str]
    order: str

    # Queries
    all_query: str = 'set/list/all'
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

    # All sets with pagination and filtering
    def all_filtered_paginated(
        self,
        search_query: str | None = None,
        page: int = 1,
        per_page: int = 50,
        sort_field: str | None = None,
        sort_order: str = 'asc',
        status_filter: str | None = None,
        theme_filter: str | None = None,
        owner_filter: str | None = None,
        purchase_location_filter: str | None = None,
        storage_filter: str | None = None,
        tag_filter: str | None = None
    ) -> tuple[Self, int]:
        # Convert theme name to theme ID for filtering
        theme_id_filter = None
        if theme_filter:
            theme_id_filter = self._theme_name_to_id(theme_filter)

        # Check if any filters are applied
        has_filters = any([status_filter, theme_id_filter, owner_filter, purchase_location_filter, storage_filter, tag_filter])

        # Prepare filter context
        filter_context = {
            'search_query': search_query,
            'status_filter': status_filter,
            'theme_filter': theme_id_filter,  # Use converted theme ID
            'owner_filter': owner_filter,
            'purchase_location_filter': purchase_location_filter,
            'storage_filter': storage_filter,
            'tag_filter': tag_filter,
            'owners': BrickSetOwnerList.as_columns(),
            'statuses': BrickSetStatusList.as_columns(),
            'tags': BrickSetTagList.as_columns(),
        }

        # Field mapping for sorting
        field_mapping = {
            'set': '"rebrickable_sets"."set"',
            'name': '"rebrickable_sets"."name"',
            'year': '"rebrickable_sets"."year"',
            'parts': '"rebrickable_sets"."number_of_parts"',
            'theme': '"rebrickable_sets"."theme_id"',
            'minifigures': '"total_minifigures"',  # Use the alias from the SQL query
            'missing': '"total_missing"',  # Use the alias from the SQL query
            'damaged': '"total_damaged"',  # Use the alias from the SQL query
            'purchase-date': '"bricktracker_sets"."purchase_date"',
            'purchase-price': '"bricktracker_sets"."purchase_price"'
        }

        # Choose query based on whether filters are applied
        query_to_use = 'set/list/all_filtered' if has_filters else self.all_query

        # Handle instructions filtering separately (post-SQL filtering)
        instructions_filter = None
        if status_filter in ['has-missing-instructions', '-has-missing-instructions']:
            instructions_filter = status_filter
            # Remove from SQL context to avoid SQL errors
            filter_context['status_filter'] = None
            # Recalculate has_filters without instructions
            has_filters = any([theme_id_filter, owner_filter, purchase_location_filter, storage_filter, tag_filter])
            query_to_use = 'set/list/all_filtered' if has_filters else self.all_query

        # Use the base pagination method with custom list method
        result, total_count = self.paginate(
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_order=sort_order,
            list_query=query_to_use,
            field_mapping=field_mapping,
            **filter_context
        )

        # Apply instructions filtering after SQL query
        if instructions_filter:
            result, total_count = self._filter_by_instructions(result, total_count, instructions_filter, page, per_page)

        # Populate themes for filter dropdown (always needed)
        result._populate_themes()

        return result, total_count

    def _populate_themes(self) -> None:
        """Populate themes list from the current records"""
        themes = set()
        for record in self.records:
            if hasattr(record, 'theme') and hasattr(record.theme, 'name'):
                themes.add(record.theme.name)

        self.themes = list(themes)
        self.themes.sort()

    def _theme_name_to_id(self, theme_name: str) -> str | None:
        """Convert a theme name to theme ID for filtering"""
        try:
            theme_list = BrickThemeList()
            for theme_id, theme in theme_list.themes.items():
                if theme.name.lower() == theme_name.lower():
                    return str(theme_id)
            return None
        except Exception:
            # If themes can't be loaded, return None to disable theme filtering
            return None

    def _filter_by_instructions(self, result_list: Self, total_count: int, instructions_filter: str, page: int, per_page: int) -> tuple[Self, int]:
        """Filter sets by instruction file existence (post-SQL filtering)"""
        try:
            # Load instructions list
            instructions_list = BrickInstructionsList()
            instruction_sets = set(instructions_list.sets.keys())

            # Filter the records
            filtered_records = []
            for record in result_list.records:
                set_id = record.fields.set
                has_instructions = set_id in instruction_sets

                if instructions_filter == 'has-missing-instructions':
                    # Show sets that are MISSING instructions
                    if not has_instructions:
                        filtered_records.append(record)
                elif instructions_filter == '-has-missing-instructions':
                    # Show sets that HAVE instructions
                    if has_instructions:
                        filtered_records.append(record)

            # Create new result with filtered records
            new_result = BrickSetList()
            new_result.records = filtered_records

            # Note: This breaks proper pagination since we're filtering after SQL
            # The total_count and pagination will be approximate
            # For proper pagination, we'd need a database table for instructions
            # This will be implemented in future versions

            return new_result, len(filtered_records)

        except Exception:
            # If instructions can't be loaded, return original results
            return result_list, total_count

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
            **context
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
