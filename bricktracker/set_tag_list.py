import logging
from typing import Self

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

    # Instantiate the list with the proper class
    @classmethod
    def new(cls, /, *, force: bool = False) -> Self:
        return cls(BrickSetTag, force=force)
