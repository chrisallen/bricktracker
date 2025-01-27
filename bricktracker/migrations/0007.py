from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..sql import BrickSQL


# Grab the list of checkboxes to create a list of SQL columns
def migration_0007(self: 'BrickSQL') -> dict[str, Any]:
    records = self.fetchall('checkbox/list')

    return {
        'sources': ', '.join([
            '"bricktracker_set_statuses_old"."status_{id}"'.format(id=record['id'])  # noqa: E501
            for record
            in records
        ]),
        'targets': ', '.join([
            '"status_{id}"'.format(id=record['id'])
            for record
            in records
        ]),
        'structure': ', '.join([
            '"status_{id}" BOOLEAN NOT NULL DEFAULT 0'.format(id=record['id'])
            for record
            in records
        ])
    }
