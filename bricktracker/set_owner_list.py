import logging

from .metadata_list import BrickMetadataList
from .set_owner import BrickSetOwner

logger = logging.getLogger(__name__)


# Lego sets owner list
class BrickSetOwnerList(BrickMetadataList[BrickSetOwner]):
    kind: str = 'set owners'

    # Database table
    table: str = 'bricktracker_set_owners'

    # Queries
    select_query = 'set/metadata/owner/list'
