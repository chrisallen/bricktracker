import logging
from typing import Any, List, overload, Self, Type, TypeVar

from flask import url_for

from .exceptions import ErrorException, NotFoundException
from .fields import BrickRecordFields
from .record_list import BrickRecordList
from .set_custom_field import BrickSetCustomField
from .set_owner import BrickSetOwner
from .set_purchase_location import BrickSetPurchaseLocation
from .set_status import BrickSetStatus
from .set_storage import BrickSetStorage
from .set_tag import BrickSetTag
from .wish_owner import BrickWishOwner

logger = logging.getLogger(__name__)

T = TypeVar(
    'T',
    BrickSetCustomField,
    BrickSetOwner,
    BrickSetPurchaseLocation,
    BrickSetStatus,
    BrickSetStorage,
    BrickSetTag,
    BrickWishOwner
)


# Lego sets metadata list
class BrickMetadataList(BrickRecordList[T]):
    kind: str
    mapping: dict[str, T]
    model: Type[T]

    # Database
    table: str
    order: str

    # Queries
    select_query: str

    # Set endpoints
    set_state_endpoint: str
    set_value_endpoint: str

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
            self.override()

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
                for record in self.select(order=self.order):
                    metadata = model(record=record)

                    self.__class__.records.append(metadata)
                    self.__class__.mapping[metadata.fields.id] = metadata

    # HTML prefix name
    def as_prefix(self, /) -> str:
        return self.kind.replace(' ', '-')

    # Filter the list of records (this one does nothing)
    def filter(self) -> list[T]:
        return self.records

    # Add a layer of override data
    def override(self) -> None:
        self.fields = BrickRecordFields()

        self.records = []
        self.mapping = {}

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

    # Return the items as a dictionary mapping column names to UUIDs
    @classmethod
    def as_column_mapping(cls, /, **kwargs) -> dict:
        new = cls.new()

        return {
            record.as_column(): record.fields.id
            for record in new.filter(**kwargs)
        }

    # Grab a specific status
    @classmethod
    def get(cls, id: str | None, /, *, allow_none: bool = False) -> T:
        new = cls.new()

        if allow_none and (id == '' or id is None):
            return new.model()

        if id is None:
            raise ErrorException('Cannot get {kind} with no ID'.format(
                kind=new.kind.capitalize()
            ))

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

    # URL to change the selected value of this metadata item for a set
    @classmethod
    def url_for_set_value(cls, id: str, /) -> str:
        return url_for(
            cls.set_value_endpoint,
            id=id,
        )

    # URL to change the selected value of this metadata item for an individual part
    @classmethod
    def url_for_individual_part_value(cls, part_id: str, /) -> str:
        # Replace 'set' with 'individual_part' in the endpoint name
        endpoint = cls.set_value_endpoint.replace('set.', 'individual_part.')
        return url_for(
            endpoint,
            id=part_id,
        )

    # URL to change the selected value of this metadata item for an individual minifigure
    @classmethod
    def url_for_individual_minifigure_value(cls, minifigure_id: str, /) -> str:
        # Replace 'set' with 'individual_minifigure' in the endpoint name
        endpoint = cls.set_value_endpoint.replace('set.', 'individual_minifigure.')
        return url_for(
            endpoint,
            id=minifigure_id,
        )


# Owner and tag filter values are interpolated into queries as column names, which
# no amount of quoting makes safe. Only values naming metadata we already know about
# are allowed through, anything else is dropped and the filter does not apply.
#
# Values look like "owner-<id>", or "-owner-<id>" for the != form.
def known_metadata_filter(
    value: str | None,
    kind: str,
    items: list,
    /,
) -> str | None:
    if not value:
        return None

    candidate = value[1:] if value.startswith('-') else value

    if not candidate.startswith('{kind}-'.format(kind=kind)):
        return None

    if candidate not in {item.as_dataset() for item in items}:
        logger.warning('Ignoring unknown {kind} filter: {value}'.format(
            kind=kind,
            value=value,
        ))

        return None

    return value


# Custom field filters arrive as one query arg per defined field:
# custom_field_<id>=<value>, or custom_field_<id>=-<value> for the != form. Unlike
# owner/tag, the id itself never needs validating against user input: this only ever
# loops over fields we already know about, so an unknown id can never get in.
def custom_field_filters_from_request(
    args: Any,
    fields: list,
    /,
) -> dict[str, str]:
    filters: dict[str, str] = {}

    for field in fields:
        value = args.get('custom_field_{id}'.format(id=field.fields.id))

        if value and value != 'all':
            filters[field.fields.id] = value

    return filters
