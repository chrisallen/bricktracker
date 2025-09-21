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

        # Handle instructions filtering
        if status_filter in ['has-missing-instructions', '-has-missing-instructions']:
            # For instructions filter, we need to load all sets first, then filter and paginate
            return self._all_filtered_paginated_with_instructions(
                search_query, page, per_page, sort_field, sort_order,
                status_filter, theme_id_filter, owner_filter,
                purchase_location_filter, storage_filter, tag_filter
            )

        # Normal SQL-based filtering and pagination
        result, total_count = self.paginate(
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_order=sort_order,
            list_query=query_to_use,
            field_mapping=field_mapping,
            **filter_context
        )

        # Populate themes for filter dropdown from ALL sets, not just current page
        result._populate_themes_global()

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

    def _all_filtered_paginated_with_instructions(
        self,
        search_query: str | None,
        page: int,
        per_page: int,
        sort_field: str | None,
        sort_order: str,
        status_filter: str,
        theme_id_filter: str | None,
        owner_filter: str | None,
        purchase_location_filter: str | None,
        storage_filter: str | None,
        tag_filter: str | None
    ) -> tuple[Self, int]:
        """Handle filtering when instructions filter is involved"""
        try:
            # Load all sets first (without pagination) with full metadata
            all_sets = BrickSetList()
            filter_context = {
                'owners': BrickSetOwnerList.as_columns(),
                'statuses': BrickSetStatusList.as_columns(),
                'tags': BrickSetTagList.as_columns(),
            }
            all_sets.list(do_theme=True, **filter_context)

            # Load instructions list
            instructions_list = BrickInstructionsList()
            instruction_sets = set(instructions_list.sets.keys())

            # Apply all filters manually
            filtered_records = []
            for record in all_sets.records:
                # Apply instructions filter
                set_id = record.fields.set
                has_instructions = set_id in instruction_sets

                if status_filter == 'has-missing-instructions' and has_instructions:
                    continue  # Skip sets that have instructions
                elif status_filter == '-has-missing-instructions' and not has_instructions:
                    continue  # Skip sets that don't have instructions

                # Apply other filters manually
                if search_query and not self._matches_search(record, search_query):
                    continue
                if theme_id_filter and not self._matches_theme(record, theme_id_filter):
                    continue
                if owner_filter and not self._matches_owner(record, owner_filter):
                    continue
                if purchase_location_filter and not self._matches_purchase_location(record, purchase_location_filter):
                    continue
                if storage_filter and not self._matches_storage(record, storage_filter):
                    continue
                if tag_filter and not self._matches_tag(record, tag_filter):
                    continue

                filtered_records.append(record)

            # Apply sorting
            if sort_field:
                filtered_records = self._sort_records(filtered_records, sort_field, sort_order)

            # Calculate pagination
            total_count = len(filtered_records)
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            paginated_records = filtered_records[start_index:end_index]

            # Create result
            result = BrickSetList()
            result.records = paginated_records

            # Copy themes from the source that has all sets
            result.themes = all_sets.themes if hasattr(all_sets, 'themes') else []

            # If themes weren't populated, populate them globally
            if not result.themes:
                result._populate_themes_global()

            return result, total_count

        except Exception:
            # Fall back to normal pagination without instructions filter
            return self.all_filtered_paginated(
                search_query, page, per_page, sort_field, sort_order,
                None, theme_id_filter, owner_filter,
                purchase_location_filter, storage_filter, tag_filter
            )

    def _populate_themes_global(self) -> None:
        """Populate themes list from ALL sets, not just current page"""
        try:
            # Load all sets to get all possible themes
            all_sets = BrickSetList().all()
            themes = set()
            for record in all_sets.records:
                if hasattr(record, 'theme') and hasattr(record.theme, 'name'):
                    themes.add(record.theme.name)

            self.themes = list(themes)
            self.themes.sort()
        except Exception:
            # Fall back to current page themes
            self._populate_themes()

    def _matches_search(self, record, search_query: str) -> bool:
        """Check if record matches search query"""
        search_lower = search_query.lower()
        return (search_lower in record.fields.name.lower() or
                search_lower in record.fields.set.lower())

    def _matches_theme(self, record, theme_id: str) -> bool:
        """Check if record matches theme filter"""
        return str(record.fields.theme_id) == theme_id

    def _matches_owner(self, record, owner_filter: str) -> bool:
        """Check if record matches owner filter"""
        if not owner_filter.startswith('owner-'):
            return True

        # Convert owner-uuid format to owner_uuid column name
        owner_column = owner_filter.replace('-', '_')

        # Check if record has this owner attribute set to 1
        return hasattr(record.fields, owner_column) and getattr(record.fields, owner_column) == 1

    def _matches_purchase_location(self, record, location_filter: str) -> bool:
        """Check if record matches purchase location filter"""
        return record.fields.purchase_location == location_filter

    def _matches_storage(self, record, storage_filter: str) -> bool:
        """Check if record matches storage filter"""
        return record.fields.storage == storage_filter

    def _matches_tag(self, record, tag_filter: str) -> bool:
        """Check if record matches tag filter"""
        if not tag_filter.startswith('tag-'):
            return True

        # Convert tag-uuid format to tag_uuid column name
        tag_column = tag_filter.replace('-', '_')

        # Check if record has this tag attribute set to 1
        return hasattr(record.fields, tag_column) and getattr(record.fields, tag_column) == 1

    def _sort_records(self, records, sort_field: str, sort_order: str):
        """Sort records manually"""
        reverse = sort_order == 'desc'

        if sort_field == 'set':
            return sorted(records, key=lambda r: r.fields.set, reverse=reverse)
        elif sort_field == 'name':
            return sorted(records, key=lambda r: r.fields.name, reverse=reverse)
        elif sort_field == 'year':
            return sorted(records, key=lambda r: r.fields.year, reverse=reverse)
        elif sort_field == 'parts':
            return sorted(records, key=lambda r: r.fields.number_of_parts, reverse=reverse)
        # Add more sort fields as needed

        return records

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
