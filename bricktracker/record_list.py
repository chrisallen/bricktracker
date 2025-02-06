from sqlite3 import Row
from typing import Any, Generator, Generic, ItemsView, TypeVar, TYPE_CHECKING

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
