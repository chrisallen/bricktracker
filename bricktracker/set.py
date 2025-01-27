import logging
import traceback
from typing import Any, Self
from uuid import uuid4

from flask import current_app, url_for

from .exceptions import DatabaseException, NotFoundException
from .minifigure_list import BrickMinifigureList
from .part_list import BrickPartList
from .rebrickable_minifigures import RebrickableMinifigures
from .rebrickable_parts import RebrickableParts
from .rebrickable_set import RebrickableSet
from .set_checkbox import BrickSetCheckbox
from .set_checkbox_list import BrickSetCheckboxList
from .sql import BrickSQL

logger = logging.getLogger(__name__)


# Lego brick set
class BrickSet(RebrickableSet):
    # Queries
    select_query: str = 'set/select/full'
    light_query: str = 'set/select/light'
    insert_query: str = 'set/insert'

    # Delete a set
    def delete(self, /) -> None:
        BrickSQL().executescript(
            'set/delete/set',
            id=self.fields.id
        )

    # Import a set into the database
    def download(self, data: dict[str, Any], /) -> None:
        # Load the set
        if not self.load(data, from_download=True):
            return

        try:
            # Insert into the database
            self.socket.auto_progress(
                message='Set {number}: inserting into database'.format(
                    number=self.fields.set
                ),
                increment_total=True,
            )

            # Generate an UUID for self
            self.fields.id = str(uuid4())

            # Insert into database
            self.insert(commit=False)

            # Execute the parent download method
            self.insert_rebrickable()

            # Load the inventory
            RebrickableParts(self.socket, self).download()

            # Load the minifigures
            RebrickableMinifigures(self.socket, self).download()

            # Commit the transaction to the database
            self.socket.auto_progress(
                message='Set {number}: writing to the database'.format(
                    number=self.fields.set
                ),
                increment_total=True,
            )

            BrickSQL().commit()

            # Info
            logger.info('Set {number}: imported (id: {id})'.format(
                number=self.fields.set,
                id=self.fields.id,
            ))

            # Complete
            self.socket.complete(
                message='Set {number}: imported (<a href="{url}">Go to the set</a>)'.format(  # noqa: E501
                    number=self.fields.set,
                    url=self.url()
                ),
                download=True
            )

        except Exception as e:
            self.socket.fail(
                message='Error while importing set {number}: {error}'.format(
                    number=self.fields.set,
                    error=e,
                )
            )

            logger.debug(traceback.format_exc())

    # Insert a Rebrickable set
    def insert_rebrickable(self, /) -> None:
        self.insert()

    # Minifigures
    def minifigures(self, /) -> BrickMinifigureList:
        return BrickMinifigureList().load(self)

    # Parts
    def parts(self, /) -> BrickPartList:
        return BrickPartList().load(self)

    # Select a light set (with an id)
    def select_light(self, id: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.id = id

        # Load from database
        if not self.select(override_query=self.light_query):
            raise NotFoundException(
                'Set with ID {id} was not found in the database'.format(
                    id=self.fields.id,
                ),
            )

        return self

    # Select a specific set (with an id)
    def select_specific(self, id: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.id = id

        # Load from database
        if not self.select(
            statuses=BrickSetCheckboxList().as_columns(solo=True)
        ):
            raise NotFoundException(
                'Set with ID {id} was not found in the database'.format(
                    id=self.fields.id,
                ),
            )

        return self

    # Update a status
    def update_status(
        self,
        checkbox: BrickSetCheckbox,
        status: bool,
        /
    ) -> None:
        parameters = self.sql_parameters()
        parameters['status'] = status

        # Update the status
        rows, _ = BrickSQL().execute_and_commit(
            'set/update/status',
            parameters=parameters,
            name=checkbox.as_column(),
        )

        if rows != 1:
            raise DatabaseException('Could not update the status "{status}" for set {number} ({id})'.format(  # noqa: E501
                status=checkbox.fields.name,
                number=self.fields.set,
                id=self.fields.id,
            ))

    # Self url
    def url(self, /) -> str:
        return url_for('set.details', id=self.fields.id)

    # Deletion url
    def url_for_delete(self, /) -> str:
        return url_for('set.delete', id=self.fields.id)

    # Actual deletion url
    def url_for_do_delete(self, /) -> str:
        return url_for('set.do_delete', id=self.fields.id)

    # Compute the url for the set instructions
    def url_for_instructions(self, /) -> str:
        if (
            not current_app.config['HIDE_SET_INSTRUCTIONS'] and
            len(self.instructions)
        ):
            return url_for(
                'set.details',
                id=self.fields.id,
                open_instructions=True
            )
        else:
            return ''
