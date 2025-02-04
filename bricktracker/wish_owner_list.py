from typing import Self

from .metadata_list import BrickMetadataList
from .wish_owner import BrickWishOwner


# Lego sets owner list
class BrickWishOwnerList(BrickMetadataList[BrickWishOwner]):
    kind: str = 'wish owners'

    # Database
    table: str = 'bricktracker_wish_owners'
    order: str = '"bricktracker_metadata_owners"."name"'

    # Queries
    select_query = 'set/metadata/owner/list'

    # Instantiate the list with the proper class
    @classmethod
    def new(cls, /, *, force: bool = False) -> Self:
        return cls(BrickWishOwner, force=force)
