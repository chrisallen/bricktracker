from .metadata import BrickMetadata

from flask import url_for


# Lego set purchase location metadata
class BrickSetPurchaseLocation(BrickMetadata):
    kind: str = 'purchase location'

    # Queries
    delete_query: str = 'set/metadata/purchase_location/delete'
    insert_query: str = 'set/metadata/purchase_location/insert'
    select_query: str = 'set/metadata/purchase_location/select'
    update_field_query: str = 'set/metadata/purchase_location/update/field'
    update_set_value_query: str = 'set/metadata/purchase_location/update/value'

    # Self url
    def url(self, /) -> str:
        return url_for(
            'purchase_location.details',
            id=self.fields.id,
        )
