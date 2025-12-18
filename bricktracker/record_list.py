import re
from sqlite3 import Row
from typing import Any, Generator, Generic, ItemsView, Self, TypeVar, TYPE_CHECKING

from .fields import BrickRecordFields
from .sql import BrickSQL
if TYPE_CHECKING:
    from .minifigure import BrickMinifigure
    from .part import BrickPart
    from .rebrickable_set import RebrickableSet
    from .set import BrickSet
    from .set_owner import BrickSetOwner
    from .set_purchase_location import BrickSetPurchaseLocation
    from .set_status import BrickSetStatus
    from .set_storage import BrickSetStorage
    from .set_tag import BrickSetTag
    from .wish import BrickWish
    from .wish_owner import BrickWishOwner

T = TypeVar(
    'T',
    'BrickMinifigure',
    'BrickPart',
    'BrickSet',
    'BrickSetOwner',
    'BrickSetPurchaseLocation',
    'BrickSetStatus',
    'BrickSetStorage',
    'BrickSetTag',
    'BrickWish',
    'BrickWishOwner',
    'RebrickableSet'
)


# SQLite records
class BrickRecordList(Generic[T]):
    select_query: str
    records: list[T]

    # Fields
    fields: BrickRecordFields

    def __init__(self, /):
        self.fields = BrickRecordFields()
        self.records = []

    # Shorthand to field items
    def items(self, /) -> ItemsView[str, Any]:
        return self.fields.__dict__.items()

    # Get all from the database
    def select(
        self,
        /,
        *,
        override_query: str | None = None,
        order: str | None = None,
        limit: int | None = None,
        **context: Any,
    ) -> list[Row]:
        # Select the query
        if override_query:
            query = override_query
        else:
            query = self.select_query

        return BrickSQL().fetchall(
            query,
            parameters=self.sql_parameters(),
            order=order,
            limit=limit,
            **context
        )

    # Generic pagination method for all record lists
    def paginate(
        self,
        page: int = 1,
        per_page: int = 50,
        sort_field: str | None = None,
        sort_order: str = 'asc',
        count_query: str | None = None,
        list_query: str | None = None,
        field_mapping: dict[str, str] | None = None,
        **filter_context: Any
    ) -> tuple['Self', int]:
        """Generic pagination implementation for all record lists"""
        from .sql import BrickSQL

        # Use provided queries or fall back to defaults
        list_query = list_query or getattr(self, 'all_query', None)
        if not list_query:
            raise NotImplementedError("Subclass must define all_query")

        # Calculate offset
        offset = (page - 1) * per_page

        # Get total count by wrapping the main query
        if count_query:
            # Use provided count query
            count_result = BrickSQL().fetchone(count_query, **filter_context)
            total_count = count_result['total_count'] if count_result else 0
        else:
            # Generate count by wrapping the main query (without ORDER BY, LIMIT, OFFSET)
            count_context = {k: v for k, v in filter_context.items()
                           if k not in ['order', 'limit', 'offset']}

            # Get the main query SQL without pagination clauses
            main_sql = BrickSQL().load_query(list_query, **count_context)

            # Remove ORDER BY, LIMIT, OFFSET clauses for counting
            # Remove ORDER BY clause and everything after it that's not part of subqueries
            count_sql = re.sub(r'\s+ORDER\s+BY\s+[^)]*?(\s+LIMIT|\s+OFFSET|$)', r'\1', main_sql, flags=re.IGNORECASE)
            # Remove LIMIT and OFFSET
            count_sql = re.sub(r'\s+LIMIT\s+\d+', '', count_sql, flags=re.IGNORECASE)
            count_sql = re.sub(r'\s+OFFSET\s+\d+', '', count_sql, flags=re.IGNORECASE)

            # Wrap in COUNT(*)
            wrapped_sql = f"SELECT COUNT(*) as total_count FROM ({count_sql.strip()})"

            count_result = BrickSQL().raw_execute(wrapped_sql, {}).fetchone()
            total_count = count_result['total_count'] if count_result else 0

        # Prepare sort order
        order_clause = None
        if sort_field and field_mapping and sort_field in field_mapping:
            sql_field = field_mapping[sort_field]
            direction = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
            order_clause = f'{sql_field} {direction}'

        # Build pagination context
        pagination_context = {
            'limit': per_page,
            'offset': offset,
            'order': order_clause or getattr(self, 'order', None),
            **filter_context
        }

        # Load paginated results using the existing list() method
        # Check if this is a set list that needs do_theme parameter
        if hasattr(self, 'themes'):  # Only BrickSetList has this attribute
            self.list(override_query=list_query, do_theme=True, **pagination_context)
        else:
            self.list(override_query=list_query, **pagination_context)

        return self, total_count

    # Base method that subclasses can override
    def list(
        self,
        /,
        *,
        override_query: str | None = None,
        **context: Any,
    ) -> None:
        """Load records from database - should be implemented by subclasses that use pagination"""
        raise NotImplementedError("Subclass must implement list() method")

    # Generic SQL parameters from fields
    def sql_parameters(self, /) -> dict[str, Any]:
        parameters: dict[str, Any] = {}
        for name, value in self.items():
            parameters[name] = value

        return parameters

    # Make the list iterable
    def __iter__(self, /) -> Generator[T, Any, Any]:
        for record in self.records:
            yield record

    # Make the list measurable
    def __len__(self, /) -> int:
        return len(self.records)
