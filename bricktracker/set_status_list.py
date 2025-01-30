import logging

from .metadata_list import BrickMetadataList
from .set_status import BrickSetStatus

logger = logging.getLogger(__name__)


# Lego sets status list
class BrickSetStatusList(BrickMetadataList):
    kind: str = 'set statuses'

    # Database table
    table: str = 'bricktracker_set_statuses'

    # Queries
    select_query = 'set/metadata/status/list'

    # Filter the list of set status
    def filter(self, all: bool = False) -> list[BrickSetStatus]:
        return [
            record
            for record
            in self.records
            if all or record.fields.displayed_on_grid
        ]
