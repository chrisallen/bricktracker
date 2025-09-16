import logging
from typing import Any, Self, TYPE_CHECKING
import traceback

from flask import current_app

from .part import BrickPart
from .rebrickable import Rebrickable
from .record_list import BrickRecordList
if TYPE_CHECKING:
    from .minifigure import BrickMinifigure
    from .set import BrickSet
    from .socket import BrickSocket

logger = logging.getLogger(__name__)


# Lego set or minifig parts
class BrickPartList(BrickRecordList[BrickPart]):
    brickset: 'BrickSet | None'
    minifigure: 'BrickMinifigure | None'
    order: str

    # Queries
    all_query: str = 'part/list/all'
    all_by_owner_query: str = 'part/list/all_by_owner'
    all_count_query: str = 'part/count/all'
    all_by_owner_count_query: str = 'part/count/all_by_owner'
    different_color_query = 'part/list/with_different_color'
    last_query: str = 'part/list/last'
    minifigure_query: str = 'part/list/from_minifigure'
    problem_query: str = 'part/list/problem'
    print_query: str = 'part/list/from_print'
    select_query: str = 'part/list/specific'

    def __init__(self, /):
        super().__init__()

        # Placeholders
        self.brickset = None
        self.minifigure = None

        # Store the order for this list
        self.order = current_app.config['PARTS_DEFAULT_ORDER']

    # Load all parts
    def all(self, /) -> Self:
        self.list(override_query=self.all_query)

        return self

    # Load all parts by owner
    def all_by_owner(self, owner_id: str | None = None, /) -> Self:
        # Save the owner_id parameter
        self.fields.owner_id = owner_id

        # Load the parts from the database
        self.list(override_query=self.all_by_owner_query)

        return self

    # Load all parts with filters (owner and/or color)
    def all_filtered(self, owner_id: str | None = None, color_id: str | None = None, /) -> Self:
        # Save the filter parameters
        if owner_id is not None:
            self.fields.owner_id = owner_id
        if color_id is not None:
            self.fields.color_id = color_id

        # Choose query based on whether owner filtering is needed
        if owner_id and owner_id != 'all':
            query = self.all_by_owner_query
        else:
            query = self.all_query

        # Load the parts from the database
        self.list(override_query=query)

        return self

    # Load parts with pagination support
    def all_filtered_paginated(
        self,
        owner_id: str | None = None,
        color_id: str | None = None,
        search_query: str | None = None,
        page: int = 1,
        per_page: int = 50,
        sort_field: str | None = None,
        sort_order: str = 'asc'
    ) -> tuple[Self, int]:
        from .sql import BrickSQL

        # Save the filter parameters
        if owner_id is not None:
            self.fields.owner_id = owner_id
        if color_id is not None:
            self.fields.color_id = color_id
        if search_query:
            self.fields.search_query = search_query
        if sort_field:
            self.fields.sort_field = sort_field
            self.fields.sort_order = sort_order

        # Calculate offset
        offset = (page - 1) * per_page

        # Get total count first
        count_context = {}
        if owner_id and owner_id != 'all':
            count_context['owner_id'] = owner_id
            count_query = self.all_by_owner_count_query
            query = self.all_by_owner_query
        else:
            count_query = self.all_count_query
            query = self.all_query

        if color_id and color_id != 'all':
            count_context['color_id'] = color_id
        if search_query:
            count_context['search_query'] = search_query

        # Execute count query
        count_result = BrickSQL().fetchone(count_query, **count_context)
        total_count = count_result['total_count'] if count_result else 0

        # Prepare sort order
        order_clause = None
        if sort_field:
            # Map frontend sort field names to SQL column names
            field_mapping = {
                'name': '"rebrickable_parts"."name"',
                'color': '"rebrickable_parts"."color_name"',
                'quantity': '"total_quantity"',
                'missing': '"total_missing"',
                'damaged': '"total_damaged"',
                'sets': '"total_sets"',
                'minifigures': '"total_minifigures"'
            }

            if sort_field in field_mapping:
                sql_field = field_mapping[sort_field]
                direction = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
                order_clause = f'{sql_field} {direction}'

        # Load paginated parts
        self.list(override_query=query, limit=per_page, offset=offset, order=order_clause)

        return self, total_count

    # Base part list
    def list(
        self,
        /,
        *,
        override_query: str | None = None,
        order: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **context: Any,
    ) -> None:
        if order is None:
            order = self.order

        if hasattr(self, 'brickset'):
            brickset = self.brickset
        else:
            brickset = None

        if hasattr(self, 'minifigure'):
            minifigure = self.minifigure
        else:
            minifigure = None

        # Prepare template context for filtering
        context_vars = {}
        if hasattr(self.fields, 'owner_id') and self.fields.owner_id is not None:
            context_vars['owner_id'] = self.fields.owner_id
        if hasattr(self.fields, 'color_id') and self.fields.color_id is not None:
            context_vars['color_id'] = self.fields.color_id
        if hasattr(self.fields, 'search_query') and self.fields.search_query:
            context_vars['search_query'] = self.fields.search_query

        # Load the sets from the database
        for record in super().select(
            override_query=override_query,
            order=order,
            limit=limit,
            offset=offset,
            **context_vars
        ):
            part = BrickPart(
                brickset=brickset,
                minifigure=minifigure,
                record=record,
            )

            if current_app.config['SKIP_SPARE_PARTS'] and part.fields.spare:
                continue

            self.records.append(part)

    # List specific parts from a brickset or minifigure
    def list_specific(
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
        self.list()

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
        self.list(override_query=self.minifigure_query)

        return self

    # Load generic parts from a print
    def from_print(
        self,
        brickpart: BrickPart,
        /,
    ) -> Self:
        # Save the part and print
        if brickpart.fields.print is not None:
            self.fields.print = brickpart.fields.print
        else:
            self.fields.print = brickpart.fields.part

        self.fields.part = brickpart.fields.part
        self.fields.color = brickpart.fields.color

        # Load the parts from the database
        self.list(override_query=self.print_query)

        return self

    # Load problematic parts
    def problem(self, /) -> Self:
        self.list(override_query=self.problem_query)

        return self

    # Return a dict with common SQL parameters for a parts list
    def sql_parameters(self, /) -> dict[str, Any]:
        parameters: dict[str, Any] = super().sql_parameters()

        # Set id
        if self.brickset is not None:
            parameters['id'] = self.brickset.fields.id

        # Use the minifigure number if present,
        if self.minifigure is not None:
            parameters['figure'] = self.minifigure.fields.figure
        else:
            parameters['figure'] = None

        return parameters

    # Load generic parts with same base but different color
    def with_different_color(
        self,
        brickpart: BrickPart,
        /,
    ) -> Self:
        # Save the part
        self.fields.part = brickpart.fields.part
        self.fields.color = brickpart.fields.color

        # Load the parts from the database
        self.list(override_query=self.different_color_query)

        return self

    # Import the parts from Rebrickable
    @staticmethod
    def download(
        socket: 'BrickSocket',
        brickset: 'BrickSet',
        /,
        *,
        minifigure: 'BrickMinifigure | None' = None,
        refresh: bool = False
    ) -> bool:
        if minifigure is not None:
            identifier = minifigure.fields.figure
            kind = 'Minifigure'
            method = 'get_minifig_elements'
        else:
            identifier = brickset.fields.set
            kind = 'Set'
            method = 'get_set_elements'

        try:
            socket.auto_progress(
                message='{kind} {identifier}: loading parts inventory from Rebrickable'.format(  # noqa: E501
                    kind=kind,
                    identifier=identifier,
                ),
                increment_total=True,
            )

            logger.debug('rebrick.lego.{method}("{identifier}")'.format(
                method=method,
                identifier=identifier,
            ))

            inventory = Rebrickable[BrickPart](
                method,
                identifier,
                BrickPart,
                socket=socket,
                brickset=brickset,
                minifigure=minifigure,
            ).list()

            # Process each part
            number_of_parts: int = 0
            for part in inventory:
                # Count the number of parts for minifigures
                if minifigure is not None:
                    number_of_parts += part.fields.quantity

                if not part.download(socket, refresh=refresh):
                    return False

            if minifigure is not None:
                minifigure.fields.number_of_parts = number_of_parts

        except Exception as e:
            socket.fail(
                message='Error while importing {kind} {identifier} parts list: {error}'.format(  # noqa: E501
                    kind=kind,
                    identifier=identifier,
                    error=e,
                )
            )

            logger.debug(traceback.format_exc())

            return False

        return True
