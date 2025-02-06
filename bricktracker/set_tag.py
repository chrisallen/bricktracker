from .metadata import BrickMetadata


# Lego set tag metadata
class BrickSetTag(BrickMetadata):
    kind: str = 'tag'

    # Set state endpoint
    set_state_endpoint: str = 'set.update_tag'

    # Queries
    delete_query: str = 'set/metadata/tag/delete'
    insert_query: str = 'set/metadata/tag/insert'
    select_query: str = 'set/metadata/tag/select'
    update_field_query: str = 'set/metadata/tag/update/field'
    update_set_state_query: str = 'set/metadata/tag/update/state'
