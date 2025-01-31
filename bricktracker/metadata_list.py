import logging
from typing import Type, TypeVar

from .exceptions import NotFoundException
from .fields import BrickRecordFields
from .record_list import BrickRecordList
from .set_owner import BrickSetOwner
from .set_status import BrickSetStatus

logger = logging.getLogger(__name__)

T = TypeVar('T', 'BrickSetStatus', 'BrickSetOwner')


# Lego sets metadata list
class BrickMetadataList(BrickRecordList[T]):
    kind: str
    mapping: dict[str, T]
    model: Type[T]

    # Database table
    table: str

    # Queries
    select_query: str

    def __init__(self, model: Type[T], /, *, force: bool = False):
        # Load statuses only if there is none already loaded
        records = getattr(self, 'records', None)

        if records is None or force:
            # Don't use super()__init__ as it would mask class variables
            self.fields = BrickRecordFields()

            logger.info('Loading {kind} list'.format(
                kind=self.kind
            ))

            self.__class__.records = []
            self.__class__.mapping = {}

            # Load the statuses from the database
            for record in self.select():
                status = model(record=record)

                self.__class__.records.append(status)
                self.__class__.mapping[status.fields.id] = status

    # Return the items as columns for a select
    def as_columns(self, /, **kwargs) -> str:
        return ', '.join([
            '"{table}"."{column}"'.format(
                table=self.table,
                column=record.as_column(),
            )
            for record
            in self.filter(**kwargs)
        ])

    # Filter the list of records (this one does nothing)
    def filter(self) -> list[T]:
        return self.records

    # Grab a specific status
    def get(self, id: str, /) -> T:
        if id not in self.mapping:
            raise NotFoundException(
                '{kind} with ID {id} was not found in the database'.format(
                    kind=self.kind.capitalize(),
                    id=id,
                ),
            )

        return self.mapping[id]

    # Get the list of statuses depending on the context
    def list(self, /, **kwargs) -> list[T]:
        return self.filter(**kwargs)
