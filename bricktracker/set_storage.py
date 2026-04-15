from .metadata import BrickMetadata
from .exceptions import ErrorException
from .sql import BrickSQL

from flask import url_for


# Lego set storage metadata
class BrickSetStorage(BrickMetadata):
    kind: str = 'storage'

    # Queries
    delete_query: str = 'set/metadata/storage/delete'
    insert_query: str = 'set/metadata/storage/insert'
    select_query: str = 'set/metadata/storage/select'
    update_field_query: str = 'set/metadata/storage/update/field'
    update_set_value_query: str = 'set/metadata/storage/update/value'
    count_usage_query: str = 'set/metadata/storage/count_usage'

    # Self url
    def url(self, /) -> str:
        return url_for(
            'storage.details',
            id=self.fields.id,
        )

    # Delete from database - check if storage is in use first
    def delete(self, /) -> None:
        # Check if storage is being used
        sql = BrickSQL()
        result = sql.fetchone(self.count_usage_query, parameters={'id': self.fields.id})

        if result:
            sets_count = result[0]
            minifigures_count = result[1]
            parts_count = result[2]
            lots_count = result[3]

            total_count = sets_count + minifigures_count + parts_count + lots_count

            if total_count > 0:
                # Build error message with counts and link
                error_parts = []
                if sets_count > 0:
                    error_parts.append('{count} set{plural}'.format(
                        count=sets_count,
                        plural='s' if sets_count != 1 else ''
                    ))
                if minifigures_count > 0:
                    error_parts.append('{count} individual minifigure{plural}'.format(
                        count=minifigures_count,
                        plural='s' if minifigures_count != 1 else ''
                    ))
                if parts_count > 0:
                    error_parts.append('{count} individual part{plural}'.format(
                        count=parts_count,
                        plural='s' if parts_count != 1 else ''
                    ))
                if lots_count > 0:
                    error_parts.append('{count} part lot{plural}'.format(
                        count=lots_count,
                        plural='s' if lots_count != 1 else ''
                    ))

                error_message = 'Cannot delete storage location "{name}". You need to remove {items} from this storage before it can be deleted. <a href="{url}">View storage details</a>'.format(
                    name=self.fields.name,
                    items=', '.join(error_parts),
                    url=self.url()
                )

                raise ErrorException(error_message)

        # If not in use, proceed with deletion
        super().delete()
