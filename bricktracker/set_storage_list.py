import logging
from typing import Self

from .metadata_list import BrickMetadataList
from .set_storage import BrickSetStorage

logger = logging.getLogger(__name__)


# Lego sets storage list
class BrickSetStorageList(BrickMetadataList[BrickSetStorage]):
    kind: str = 'set storages'

    # Queries
    select_query = 'set/metadata/storage/list'

    # Set state endpoint
    set_state_endpoint: str = 'set.update_storage'

    # Instantiate the list with the proper class
    @classmethod
    def new(cls, /, *, force: bool = False) -> Self:
        return cls(BrickSetStorage, force=force)
