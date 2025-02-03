from .metadata import BrickMetadata


# Lego set storage metadata
class BrickSetStorage(BrickMetadata):
    kind: str = 'storage'

    # Queries
    delete_query: str = 'set/metadata/storage/delete'
    insert_query: str = 'set/metadata/storage/insert'
    select_query: str = 'set/metadata/storage/select'
    update_field_query: str = 'set/metadata/storage/update/field'
    update_set_state_query: str = 'set/metadata/storage/update/state'
