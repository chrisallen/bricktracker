import logging
from typing import Any, Self, TYPE_CHECKING
import traceback

from flask import current_app

from .part import BrickPart
from .rebrickable import Rebrickable
from .record_list import BrickRecordList
if TYPE_CHECKING:
    from .minifigure import BrickMinifigure
    from .set import BrickSet
    from .socket import BrickSocket

logger = logging.getLogger(__name__)


# Lego set or minifig parts
class BrickPartList(BrickRecordList[BrickPart]):
    brickset: 'BrickSet | None'
    minifigure: 'BrickMinifigure | None'
    order: str

    # Queries
    all_query: str = 'part/list/all'
    last_query: str = 'part/list/last'
    minifigure_query: str = 'part/list/from_minifigure'
    missing_query: str = 'part/list/missing'
    print_query: str = 'part/list/from_print'
    select_query: str = 'part/list/specific'

    def __init__(self, /):
        super().__init__()

        # Placeholders
        self.brickset = None
        self.minifigure = None

        # Store the order for this list
        self.order = current_app.config['PARTS_DEFAULT_ORDER']

    # Load all parts
    def all(self, /) -> Self:
        for record in self.select(
            override_query=self.all_query,
            order=self.order
        ):
            part = BrickPart(record=record)

            self.records.append(part)

        return self

    # List specific parts from a brickset or minifigure
    def list_specific(
        self,
        brickset: 'BrickSet',
        /,
        *,
        minifigure: 'BrickMinifigure | None' = None,
    ) -> Self:
        # Save the brickset and minifigure
        self.brickset = brickset
        self.minifigure = minifigure

        # Load the parts from the database
        for record in self.select(order=self.order):
            part = BrickPart(
                brickset=self.brickset,
                minifigure=minifigure,
                record=record,
            )

            if current_app.config['SKIP_SPARE_PARTS'] and part.fields.spare:
                continue

            self.records.append(part)

        return self

    # Load generic parts from a minifigure
    def from_minifigure(
        self,
        minifigure: 'BrickMinifigure',
        /,
    ) -> Self:
        # Save the  minifigure
        self.minifigure = minifigure

        # Load the parts from the database
        for record in self.select(
            override_query=self.minifigure_query,
            order=self.order
        ):
            part = BrickPart(
                minifigure=minifigure,
                record=record,
            )

            if current_app.config['SKIP_SPARE_PARTS'] and part.fields.spare:
                continue

            self.records.append(part)

        return self

    # Load generic parts from a print
    def from_print(
        self,
        brickpart: BrickPart,
        /,
    ) -> Self:
        # Save the part and print
        if brickpart.fields.print is not None:
            self.fields.print = brickpart.fields.print
        else:
            self.fields.print = brickpart.fields.part

        self.fields.part = brickpart.fields.part
        self.fields.color = brickpart.fields.color

        # Load the parts from the database
        for record in self.select(
            override_query=self.print_query,
            order=self.order
        ):
            part = BrickPart(
                record=record,
            )

            if (
                current_app.config['SKIP_SPARE_PARTS'] and
                part.fields.spare
            ):
                continue

            self.records.append(part)

        return self

    # Load missing parts
    def missing(self, /) -> Self:
        for record in self.select(
            override_query=self.missing_query,
            order=self.order
        ):
            part = BrickPart(record=record)

            self.records.append(part)

        return self

    # Return a dict with common SQL parameters for a parts list
    def sql_parameters(self, /) -> dict[str, Any]:
        parameters: dict[str, Any] = super().sql_parameters()

        # Set id
        if self.brickset is not None:
            parameters['id'] = self.brickset.fields.id

        # Use the minifigure number if present,
        if self.minifigure is not None:
            parameters['figure'] = self.minifigure.fields.figure
        else:
            parameters['figure'] = None

        return parameters

    # Import the parts from Rebrickable
    @staticmethod
    def download(
        socket: 'BrickSocket',
        brickset: 'BrickSet',
        /,
        *,
        minifigure: 'BrickMinifigure | None' = None,
        refresh: bool = False
    ) -> bool:
        if minifigure is not None:
            identifier = minifigure.fields.figure
            kind = 'Minifigure'
            method = 'get_minifig_elements'
        else:
            identifier = brickset.fields.set
            kind = 'Set'
            method = 'get_set_elements'

        try:
            socket.auto_progress(
                message='{kind} {identifier}: loading parts inventory from Rebrickable'.format(  # noqa: E501
                    kind=kind,
                    identifier=identifier,
                ),
                increment_total=True,
            )

            logger.debug('rebrick.lego.{method}("{identifier}")'.format(
                method=method,
                identifier=identifier,
            ))

            inventory = Rebrickable[BrickPart](
                method,
                identifier,
                BrickPart,
                socket=socket,
                brickset=brickset,
                minifigure=minifigure,
            ).list()

            # Process each part
            for part in inventory:
                if not part.download(socket, refresh=refresh):
                    return False

        except Exception as e:
            socket.fail(
                message='Error while importing {kind} {identifier} parts list: {error}'.format(  # noqa: E501
                    kind=kind,
                    identifier=identifier,
                    error=e,
                )
            )

            logger.debug(traceback.format_exc())

            return False

        return True
