from typing import Self

from .metadata_list import BrickMetadataList
from .set_custom_field import BrickSetCustomField


# Lego sets custom field list
class BrickSetCustomFieldList(BrickMetadataList[BrickSetCustomField]):
    kind: str = 'set custom fields'

    # Database
    table: str = 'bricktracker_set_custom_fields'
    order: str = '"bricktracker_metadata_custom_fields"."name"'

    # Queries
    select_query: str = 'set/metadata/custom_field/list'

    # Set value endpoint
    set_value_endpoint: str = 'set.update_custom_field'

    # Instantiate the list with the proper class
    @classmethod
    def new(cls, /, *, force: bool = False) -> Self:
        return cls(BrickSetCustomField, force=force)
