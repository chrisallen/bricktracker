import logging

from .exceptions import NotFoundException
from .fields import BrickRecordFields
from .record_list import BrickRecordList
from .set_checkbox import BrickSetCheckbox

logger = logging.getLogger(__name__)


# Lego sets checkbox list
class BrickSetCheckboxList(BrickRecordList[BrickSetCheckbox]):
    checkboxes: dict[str, BrickSetCheckbox]

    # Queries
    select_query = 'checkbox/list'

    def __init__(self, /, *, force: bool = False):
        # Load checkboxes only if there is none already loaded
        records = getattr(self, 'records', None)

        if records is None or force:
            # Don't use super()__init__ as it would mask class variables
            self.fields = BrickRecordFields()

            logger.info('Loading set checkboxes list')

            BrickSetCheckboxList.records = []
            BrickSetCheckboxList.checkboxes = {}

            # Load the checkboxes from the database
            for record in self.select():
                checkbox = BrickSetCheckbox(record=record)

                BrickSetCheckboxList.records.append(checkbox)
                BrickSetCheckboxList.checkboxes[checkbox.fields.id] = checkbox

    # Return the checkboxes as columns for a select
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

    # Grab a specific checkbox
    def get(self, id: str, /) -> BrickSetCheckbox:
        if id not in self.checkboxes:
            raise NotFoundException(
                'Checkbox with ID {id} was not found in the database'.format(
                    id=self.fields.id,
                ),
            )

        return self.checkboxes[id]

    # Get the list of checkboxes depending on the context
    def list(self, /, *, all: bool = False) -> list[BrickSetCheckbox]:
        return [
            record
            for record
            in self.records
            if all or record.fields.displayed_on_grid
        ]
