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

# The filters both the parts page and the problem page offer. 'all' or empty means
# the filter is off.
FILTER_NAMES: tuple[str, ...] = (
    'owner_id',
    'color_id',
    'theme_id',
    'year',
    'storage_id',
    'tag_id',
    'status_id',
)

# Filters whose value is data and can be bound as a SQL parameter. owner, tag and
# status are missing on purpose: those become column names, so they get validated
# against the known metadata ids instead.
BOUND_FILTERS: tuple[str, ...] = ('color_id', 'theme_id', 'year', 'storage_id')

# Storage has two sentinel values on top of the real ids
STORAGE_SENTINELS: tuple[str, ...] = ('__none__', '-__none__')


# Strip the leading "-" a negated filter carries
def without_negation(value: str, /) -> str:
    return value[1:] if value.startswith('-') else value


# owner, tag and status ids are interpolated into the query as column names, which
# no amount of quoting makes safe. Only ids we already know about get through.
def known_metadata_id(value: str | None, known: set[str], /) -> str | None:
    if not value or value == 'all':
        return None

    if without_negation(value) not in known:
        logger.warning('Ignoring unknown metadata filter: {value}'.format(
            value=value,
        ))
        return None

    return value


# Lego set or minifig parts
class BrickPartList(BrickRecordList[BrickPart]):
    brickset: 'BrickSet | None'
    minifigure: 'BrickMinifigure | None'
    individual_minifigure: 'IndividualMinifigure | None'
    order: str
    filter_parameters: dict[str, Any]

    # Queries
    all_query: str = 'part/list/filtered'
    filtered_query: str = 'part/list/filtered'
    different_color_query = 'part/list/with_different_color'
    last_query: str = 'part/list/last'
    minifigure_query: str = 'part/list/from_minifigure'
    print_query: str = 'part/list/from_print'
    select_query: str = 'part/list/specific'

    # Sortable columns, shared by both pages
    field_mapping: dict[str, str] = {
        'name': '"rebrickable_parts"."name"',
        'color': '"rebrickable_parts"."color_name"',
        'quantity': '"total_quantity"',
        'missing': '"total_missing"',
        'damaged': '"total_damaged"',
        'sets': '"total_sets"',
        'minifigures': '"total_minifigures"',
    }

    def __init__(self, /):
        super().__init__()

        # Placeholders
        self.brickset = None
        self.minifigure = None
        self.filter_parameters = {}

        # Store the order for this list
        self.order = current_app.config['PARTS_DEFAULT_ORDER']

    # Build the Jinja context for the filtered query, and stash the values that get
    # bound as SQL parameters. Both pages go through here, so a filter either works
    # on both or on neither.
    def filter_context(
        self,
        /,
        *,
        problem_only: bool = False,
        individuals_filter: str | None = None,
        search_query: str | None = None,
        custom_field_filters: dict[str, str] | None = None,
        **filters: str | None,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {}

        if problem_only:
            context['problem_only'] = True

        for name in FILTER_NAMES:
            value = filters.get(name)
            if value and value != 'all':
                context[name] = value

        if individuals_filter == 'only':
            context['individuals_filter'] = True

        if search_query:
            context['search_query'] = search_query

        if custom_field_filters:
            context['custom_field_filters'] = custom_field_filters

        # Hide spare parts from display if configured
        if current_app.config.get('HIDE_SPARE_PARTS', False):
            context['skip_spare_parts'] = True

        # Everything that is data rather than a column name gets bound. The query
        # decides what "not this" means, so the value itself is bound without its
        # leading "-".
        self.filter_parameters = {}
        for name in BOUND_FILTERS:
            value = context.get(name)
            if value is None:
                continue
            if name == 'storage_id' and value in STORAGE_SENTINELS:
                continue
            self.filter_parameters[name] = without_negation(value)

        if search_query:
            self.filter_parameters['search_query'] = '%{query}%'.format(
                query=search_query.lower(),
            )

        for field_id, value in (custom_field_filters or {}).items():
            self.filter_parameters['custom_field_value_{id}'.format(id=field_id)] = without_negation(value)  # noqa: E501

        return context

    # Load parts with filters. problem_only narrows to parts with something missing
    # or damaged, which is all the /parts/problem page is.
    def filtered(
        self,
        /,
        *,
        problem_only: bool = False,
        individuals_filter: str | None = None,
        custom_field_filters: dict[str, str] | None = None,
        **filters: str | None,
    ) -> Self:
        context = self.filter_context(
            problem_only=problem_only,
            individuals_filter=individuals_filter,
            custom_field_filters=custom_field_filters,
            **filters
        )

        self.list(override_query=self.filtered_query, **context)

        return self

    # Same thing, one page at a time
    def paginated_filtered(
        self,
        /,
        *,
        problem_only: bool = False,
        individuals_filter: str | None = None,
        search_query: str | None = None,
        page: int = 1,
        per_page: int = 50,
        sort_field: str | None = None,
        sort_order: str = 'asc',
        custom_field_filters: dict[str, str] | None = None,
        **filters: str | None,
    ) -> tuple[Self, int]:
        context = self.filter_context(
            problem_only=problem_only,
            individuals_filter=individuals_filter,
            search_query=search_query,
            custom_field_filters=custom_field_filters,
            **filters
        )

        return self.paginate(
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_order=sort_order,
            list_query=self.filtered_query,
            field_mapping=self.field_mapping,
            **context
        )

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

        if hasattr(self, 'individual_minifigure'):
            individual_minifigure = self.individual_minifigure
        else:
            individual_minifigure = None

        # Load the sets from the database. Filters arrive in context, built by
        # filter_context, rather than being read back off self.fields.
        for record in super().select(
            override_query=override_query,
            order=order,
            limit=limit,
            offset=offset,
            **context
        ):
            part = BrickPart(
                brickset=brickset,
                minifigure=minifigure,
                individual_minifigure=individual_minifigure,
                record=record,
            )

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

        # Prepare context for hiding spare parts if configured
        context = {}
        if current_app.config.get('HIDE_SPARE_PARTS', False):
            context['skip_spare_parts'] = True

        # Load the parts from the database
        self.list(**context)

        return self

    # Load generic parts from a minifigure
    def from_minifigure(
        self,
        minifigure: 'BrickMinifigure',
        /,
    ) -> Self:
        # Save the  minifigure
        self.minifigure = minifigure

        # Prepare context for hiding spare parts if configured
        context = {}
        if current_app.config.get('HIDE_SPARE_PARTS', False):
            context['skip_spare_parts'] = True

        # Load the parts from the database
        self.list(override_query=self.minifigure_query, **context)

        return self

    # Load parts from an individual minifigure instance
    def from_individual_minifigure(
        self,
        individual_minifigure: 'IndividualMinifigure',
        /,
    ) -> Self:
        from .individual_minifigure import IndividualMinifigure

        # Save the individual minifigure reference
        self.individual_minifigure = individual_minifigure

        # Load the parts for this individual minifigure instance
        self.list(
            override_query='individual_minifigure/part/list/from_instance'
        )

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

    # Last added parts
    def last(self, /, *, limit: int = 6) -> Self:
        if current_app.config['RANDOM']:
            order = 'RANDOM()'
        else:
            # Since bricktracker_parts has a composite primary key, it doesn't have a rowid
            # Order by id DESC (which are UUIDs with timestamps) to get recent parts
            order = '"combined"."id" DESC, "combined"."part" ASC'

        context = {}
        if current_app.config.get('HIDE_SPARE_PARTS', False):
            context['skip_spare_parts'] = True

        self.list(override_query=self.last_query, order=order, limit=limit, **context)

        return self

    # Return a dict with common SQL parameters for a parts list
    def sql_parameters(self, /) -> dict[str, Any]:
        parameters: dict[str, Any] = super().sql_parameters()

        # Filter values that are data rather than column names
        parameters.update(self.filter_parameters)

        # Set id
        if self.brickset is not None:
            parameters['id'] = self.brickset.fields.id

        # Use the individual minifigure ID if present
        if hasattr(self, 'individual_minifigure') and self.individual_minifigure is not None:
            parameters['id'] = self.individual_minifigure.fields.id

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
            skip_spares = current_app.config.get('SKIP_SPARE_PARTS', False)

            for part in inventory:
                # Skip spare parts if configured
                if skip_spares and part.fields.spare:
                    continue

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
