import logging
from typing import Self, TYPE_CHECKING

from .record_list import BrickRecordList
from .individual_part_lot import IndividualPartLot

if TYPE_CHECKING:
    from .set_storage import BrickSetStorage

logger = logging.getLogger(__name__)


# List of individual part lots
class IndividualPartLotList(BrickRecordList):
    # Queries
    list_query: str = 'individual_part_lot/list/all'
    by_part_and_color_query: str = 'individual_part_lot/list/by_part_and_color'
    by_storage_query: str = 'individual_part_lot/list/by_storage'
    using_storage_query: str = 'individual_part_lot/list/using_storage'
    using_purchase_location_query: str = 'individual_part_lot/list/using_purchase_location'
    without_storage_query: str = 'individual_part_lot/list/without_storage'
    problem_query: str = 'individual_part_lot/list/problem'

    # Get all individual part lots
    def all(self, /) -> Self:
        self.list(override_query=self.list_query)
        return self

    # Base individual part lot list
    def list(
        self,
        /,
        *,
        override_query: str | None = None,
        order: str | None = None,
        limit: int | None = None,
        **context,
    ) -> None:
        # Load the individual part lots from the database
        for record in super().select(
            override_query=override_query,
            order=order,
            limit=limit,
            **context
        ):
            lot = IndividualPartLot(record=record)
            self.records.append(lot)

    # Set the record class
    def set_record_class(self, /) -> None:
        self.record_class = IndividualPartLot

    # Get individual part lots containing a specific part and color
    def by_part_and_color(self, part: str, color_id: int, /) -> Self:
        self.fields.part = part
        self.fields.color = color_id
        self.list(override_query='individual_part_lot/list/by_part_and_color')
        return self

    # Get individual part lots by storage location
    def by_storage(self, storage: 'BrickSetStorage', /) -> Self:
        self.fields.storage = storage.fields.id
        self.list(override_query=self.by_storage_query)
        return self

    # Get individual part lots using a specific storage location
    def using_storage(self, storage: 'BrickSetStorage', /) -> Self:
        self.fields.storage = storage.fields.id
        self.list(override_query=self.using_storage_query)
        return self

    # Get individual part lots using a specific purchase location
    def using_purchase_location(self, purchase_location: 'BrickSetPurchaseLocation', /) -> Self:
        self.fields.purchase_location = purchase_location.fields.id
        self.list(override_query=self.using_purchase_location_query)
        return self

    # Get individual part lots without storage
    def without_storage(self, /) -> Self:
        self.list(override_query=self.without_storage_query)
        return self

    # Get individual part lots with problems (containing parts with missing or damaged items)
    def with_problems(self, /) -> Self:
        self.list(override_query=self.problem_query)
        return self
