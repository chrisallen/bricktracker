import logging
from typing import List, overload, Self, Type, TypeVar

from flask import url_for

from .exceptions import NotFoundException
from .fields import BrickRecordFields
from .record_list import BrickRecordList
from .set_owner import BrickSetOwner
from .set_status import BrickSetStatus
from .set_storage import BrickSetStorage
from .set_tag import BrickSetTag

logger = logging.getLogger(__name__)

T = TypeVar('T', BrickSetOwner, BrickSetStatus, BrickSetStorage, BrickSetTag)


# Lego sets metadata list
class BrickMetadataList(BrickRecordList[T]):
    kind: str
    mapping: dict[str, T]
    model: Type[T]

    # Database table
    table: str

    # Queries
    select_query: str

    # Set state endpoint
    set_state_endpoint: str

    def __init__(
        self,
        model: Type[T],
        /,
        *,
        force: bool = False,
        records: list[T] | None = None
    ):
        self.model = model

        # Records override (masking the class variables with instance ones)
        if records is not None:
            self.records = []
            self.mapping = {}

            for metadata in records:
                self.records.append(metadata)
                self.mapping[metadata.fields.id] = metadata
        else:
            # Load metadata only if there is none already loaded
            records = getattr(self, 'records', None)

            if records is None or force:
                # Don't use super()__init__ as it would mask class variables
                self.fields = BrickRecordFields()

                logger.info('Loading {kind} list'.format(
                    kind=self.kind
                ))

                self.__class__.records = []
                self.__class__.mapping = {}

                # Load the metadata from the database
                for record in self.select():
                    metadata = model(record=record)

                    self.__class__.records.append(metadata)
                    self.__class__.mapping[metadata.fields.id] = metadata

    # HTML prefix name
    def as_prefix(self, /) -> str:
        return self.kind.replace(' ', '-')

    # Filter the list of records (this one does nothing)
    def filter(self) -> list[T]:
        return self.records

    # Return the items as columns for a select
    @classmethod
    def as_columns(cls, /, **kwargs) -> str:
        new = cls.new()

        return ', '.join([
            '"{table}"."{column}"'.format(
                table=cls.table,
                column=record.as_column(),
            )
            for record
            in new.filter(**kwargs)
        ])

    # Grab a specific status
    @classmethod
    def get(cls, id: str, /, *, allow_none: bool = False) -> T:
        new = cls.new()

        if allow_none and id == '':
            return new.model()

        if id not in new.mapping:
            raise NotFoundException(
                '{kind} with ID {id} was not found in the database'.format(
                    kind=new.kind.capitalize(),
                    id=id,
                ),
            )

        return new.mapping[id]

    # Get the list of statuses depending on the context
    @overload
    @classmethod
    def list(cls, /, **kwargs) -> List[T]: ...

    @overload
    @classmethod
    def list(cls, /, as_class: bool = False, **kwargs) -> Self: ...

    @classmethod
    def list(cls, /, as_class: bool = False, **kwargs) -> List[T] | Self:
        new = cls.new()
        list = new.filter(**kwargs)

        if as_class:
            print(list)
            # Return a copy of the metadata list with overriden records
            return cls(new.model, records=list)
        else:
            return list

    # Instantiate the list with the proper class
    @classmethod
    def new(cls, /, *, force: bool = False) -> Self:
        raise Exception('new() is not implemented for BrickMetadataList')

    # URL to change the selected state of this metadata item for a set
    @classmethod
    def url_for_set_state(cls, id: str, /) -> str:
        return url_for(
            cls.set_state_endpoint,
            id=id,
        )
