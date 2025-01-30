import logging

from .exceptions import NotFoundException
from .fields import BrickRecordFields
from .record_list import BrickRecordList
from .set_status import BrickSetStatus

logger = logging.getLogger(__name__)


# Lego sets status list
class BrickSetStatusList(BrickRecordList[BrickSetStatus]):
    statuses: dict[str, BrickSetStatus]

    # Queries
    select_query = 'set/metadata/status/list'

    def __init__(self, /, *, force: bool = False):
        # Load statuses only if there is none already loaded
        records = getattr(self, 'records', None)

        if records is None or force:
            # Don't use super()__init__ as it would mask class variables
            self.fields = BrickRecordFields()

            logger.info('Loading set statuses list')

            BrickSetStatusList.records = []
            BrickSetStatusList.statuses = {}

            # Load the statuses from the database
            for record in self.select():
                status = BrickSetStatus(record=record)

                BrickSetStatusList.records.append(status)
                BrickSetStatusList.statuses[status.fields.id] = status

    # Return the statuses as columns for a select
    def as_columns(
        self,
        /,
        *,
        solo: bool = False,
        table: str = 'bricktracker_set_statuses'
    ) -> str:
        return ', '.join([
            '"{table}"."{column}"'.format(
                table=table,
                column=record.as_column(),
            )
            for record
            in self.records
            if solo or record.fields.displayed_on_grid
        ])

    # Grab a specific status
    def get(self, id: str, /) -> BrickSetStatus:
        if id not in self.statuses:
            raise NotFoundException(
                'Status with ID {id} was not found in the database'.format(
                    id=id,
                ),
            )

        return self.statuses[id]

    # Get the list of statuses depending on the context
    def list(self, /, *, all: bool = False) -> list[BrickSetStatus]:
        return [
            record
            for record
            in self.records
            if all or record.fields.displayed_on_grid
        ]
