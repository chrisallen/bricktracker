import logging
from typing import Any, Self, TYPE_CHECKING
import traceback

from flask import url_for

from .exceptions import ErrorException, NotFoundException
from .rebrickable_part import RebrickablePart
from .sql import BrickSQL
if TYPE_CHECKING:
    from .minifigure import BrickMinifigure
    from .set import BrickSet
    from .socket import BrickSocket

logger = logging.getLogger(__name__)


# Lego set or minifig part
class BrickPart(RebrickablePart):
    identifier: str
    kind: str

    # Queries
    insert_query: str = 'part/insert'
    generic_query: str = 'part/select/generic'
    select_query: str = 'part/select/specific'

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        if self.minifigure is not None:
            self.identifier = self.minifigure.fields.figure
            self.kind = 'Minifigure'
        elif self.brickset is not None:
            self.identifier = self.brickset.fields.set
            self.kind = 'Set'

    # Import a part into the database
    def download(self, socket: 'BrickSocket', refresh: bool = False) -> bool:
        if self.brickset is None:
            raise ErrorException('Importing a part from Rebrickable outside of a set is not supported')  # noqa: E501

        try:
            # Insert into the database
            socket.auto_progress(
                message='{kind} {identifier}: inserting part {part} into database'.format(  # noqa: E501
                    kind=self.kind,
                    identifier=self.identifier,
                    part=self.fields.part
                )
            )

            if not refresh:
                # Insert into database
                self.insert(commit=False)

            # Insert the rebrickable set into database
            self.insert_rebrickable()

        except Exception as e:
            socket.fail(
                message='Error while importing part {part} from {kind} {identifier}: {error}'.format(  # noqa: E501
                    part=self.fields.part,
                    kind=self.kind,
                    identifier=self.identifier,
                    error=e,
                )
            )

            logger.debug(traceback.format_exc())

            return False

        return True

    # A identifier for HTML component
    def html_id(self, /) -> str:
        components: list[str] = ['part']

        if self.fields.figure is not None:
            components.append(self.fields.figure)

        components.append(self.fields.part)
        components.append(str(self.fields.color))
        components.append(str(self.fields.spare))

        return '-'.join(components)

    # Select a generic part
    def select_generic(
        self,
        part: str,
        color: int,
        /,
    ) -> Self:
        # Save the parameters to the fields
        self.fields.part = part
        self.fields.color = color

        if not self.select(override_query=self.generic_query):
            raise NotFoundException(
                'Part with number {number}, color ID {color} was not found in the database'.format(  # noqa: E501
                    number=self.fields.part,
                    color=self.fields.color,
                ),
            )

        return self

    # Select a specific part (with a set and an id, and option. a minifigure)
    def select_specific(
        self,
        brickset: 'BrickSet',
        part: str,
        color: int,
        spare: int,
        /,
        *,
        minifigure: 'BrickMinifigure | None' = None,
    ) -> Self:
        # Save the parameters to the fields
        self.brickset = brickset
        self.minifigure = minifigure
        self.fields.part = part
        self.fields.color = color
        self.fields.spare = spare

        if not self.select():
            if self.minifigure is not None:
                figure = self.minifigure.fields.figure
            else:
                figure = None

            raise NotFoundException(
                'Part {part} with color {color} (spare: {spare}) from set {set} ({id}) (minifigure: {figure}) was not found in the database'.format(  # noqa: E501
                    part=self.fields.part,
                    color=self.fields.color,
                    spare=self.fields.spare,
                    id=self.fields.id,
                    set=self.brickset.fields.set,
                    figure=figure,
                ),
            )

        return self

    # Update the missing part
    def update_missing(self, json: Any | None, /) -> None:
        missing = json.get('value', '')  # type: ignore

        # We need a positive integer
        try:
            if missing == '':
                missing = 0

            missing = int(missing)

            if missing < 0:
                missing = 0
        except Exception:
            raise ErrorException('"{missing}" is not a valid integer'.format(
                missing=missing
            ))

        if missing < 0:
            raise ErrorException('Cannot set a negative missing value')

        self.fields.missing = missing

        BrickSQL().execute_and_commit(
            'part/update/missing',
            parameters=self.sql_parameters()
        )

    # Compute the url for missing part
    def url_for_missing(self, /) -> str:
        # Different URL for a minifigure part
        if self.minifigure is not None:
            figure = self.minifigure.fields.figure
        else:
            figure = None

        return url_for(
            'set.missing_part',
            id=self.fields.id,
            figure=figure,
            part=self.fields.part,
            color=self.fields.color,
            spare=self.fields.spare,
        )
