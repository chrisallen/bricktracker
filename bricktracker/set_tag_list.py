import logging

from .metadata_list import BrickMetadataList
from .set_tag import BrickSetTag

logger = logging.getLogger(__name__)


# Lego sets tag list
class BrickSetTagList(BrickMetadataList[BrickSetTag]):
    kind: str = 'set tags'

    # Database table
    table: str = 'bricktracker_set_tags'

    # Queries
    select_query = 'set/metadata/tag/list'
