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
    different_color_query = 'part/list/with_different_color'
    last_query: str = 'part/list/last'
    minifigure_query: str = 'part/list/from_minifigure'
    problem_query: str = 'part/list/problem'
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
        self.list(override_query=self.all_query)

        return self

    # Base part list
    def list(
        self,
        /,
        *,
        override_query: str | None = None,
        order: str | None = None,
        limit: int | None = None,
        **context: Any,
    ) -> None:
        if order is None:
            order = self.order

        if hasattr(self, 'brickset'):
            brickset = self.brickset
        else:
            brickset = None

        if hasattr(self, 'minifigure'):
            minifigure = self.minifigure
        else:
            minifigure = None

        # Load the sets from the database
        for record in super().select(
            override_query=override_query,
            order=order,
            limit=limit,
        ):
            part = BrickPart(
                brickset=brickset,
                minifigure=minifigure,
                record=record,
            )

            if current_app.config['SKIP_SPARE_PARTS'] and part.fields.spare:
                continue

            self.records.append(part)

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
        self.list()

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
        self.list(override_query=self.minifigure_query)

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
        self.list(override_query=self.print_query)

        return self

    # Load problematic parts
    def problem(self, /) -> Self:
        self.list(override_query=self.problem_query)

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

    # Load generic parts with same base but different color
    def with_different_color(
        self,
        brickpart: BrickPart,
        /,
    ) -> Self:
        # Save the part
        self.fields.part = brickpart.fields.part
        self.fields.color = brickpart.fields.color

        # Load the parts from the database
        self.list(override_query=self.different_color_query)

        return self

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
            number_of_parts: int = 0
            for part in inventory:
                # Count the number of parts for minifigures
                if minifigure is not None:
                    number_of_parts += part.fields.quantity

                if not part.download(socket, refresh=refresh):
                    return False

            if minifigure is not None:
                minifigure.fields.number_of_parts = number_of_parts

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
