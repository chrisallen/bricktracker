import logging
import traceback
from typing import Any, Self, TYPE_CHECKING
from uuid import uuid4

from flask import current_app, url_for

from .exceptions import NotFoundException
from .minifigure_list import BrickMinifigureList
from .part_list import BrickPartList
from .rebrickable_set import RebrickableSet
from .set_owner_list import BrickSetOwnerList
from .set_status_list import BrickSetStatusList
from .set_storage_list import BrickSetStorageList
from .set_tag_list import BrickSetTagList
from .sql import BrickSQL
if TYPE_CHECKING:
    from .socket import BrickSocket

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
    def download(self, socket: 'BrickSocket', data: dict[str, Any], /) -> bool:
        # Load the set
        if not self.load(socket, data, from_download=True):
            return False

        try:
            # Insert into the database
            socket.auto_progress(
                message='Set {set}: inserting into database'.format(
                    set=self.fields.set
                ),
                increment_total=True,
            )

            # Grabbing the refresh flag
            refresh: bool = bool(data.get('refresh', False))

            # Generate an UUID for self
            self.fields.id = str(uuid4())

            if not refresh:
                # Save the storage
                storage = BrickSetStorageList.get(
                    data.get('storage', ''),
                    allow_none=True
                )
                self.fields.storage = storage.fields.id

                # Insert into database
                self.insert(commit=False)

                # Save the owners
                owners: list[str] = list(data.get('owners', []))

                for id in owners:
                    owner = BrickSetOwnerList.get(id)
                    owner.update_set_state(self, state=True)

                # Save the tags
                tags: list[str] = list(data.get('tags', []))

                for id in tags:
                    tag = BrickSetTagList.get(id)
                    tag.update_set_state(self, state=True)

            # Insert the rebrickable set into database
            self.insert_rebrickable()

            # Load the inventory
            if not BrickPartList.download(socket, self, refresh=refresh):
                return False

            # Load the minifigures
            if not BrickMinifigureList.download(socket, self, refresh=refresh):
                return False

            # Commit the transaction to the database
            socket.auto_progress(
                message='Set {set}: writing to the database'.format(
                    set=self.fields.set
                ),
                increment_total=True,
            )

            BrickSQL().commit()

            if refresh:
                # Info
                logger.info('Set {set}: imported (id: {id})'.format(
                    set=self.fields.set,
                    id=self.fields.id,
                ))

                # Complete
                socket.complete(
                    message='Set {set}: refreshed'.format(  # noqa: E501
                        set=self.fields.set,
                    ),
                    download=True
                )
            else:
                # Info
                logger.info('Set {set}: refreshed'.format(
                    set=self.fields.set,
                ))

                # Complete
                socket.complete(
                    message='Set {set}: imported (<a href="{url}">Go to the set</a>)'.format(  # noqa: E501
                        set=self.fields.set,
                        url=self.url()
                    ),
                    download=True
                )

        except Exception as e:
            socket.fail(
                message='Error while importing set {set}: {error}'.format(
                    set=self.fields.set,
                    error=e,
                )
            )

            logger.debug(traceback.format_exc())

            return False

        return True

    # Minifigures
    def minifigures(self, /) -> BrickMinifigureList:
        return BrickMinifigureList().from_set(self)

    # Parts
    def parts(self, /) -> BrickPartList:
        return BrickPartList().list_specific(self)

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
            owners=BrickSetOwnerList.as_columns(),
            statuses=BrickSetStatusList.as_columns(all=True),
            tags=BrickSetTagList.as_columns(),
        ):
            raise NotFoundException(
                'Set with ID {id} was not found in the database'.format(
                    id=self.fields.id,
                ),
            )

        return self

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

    # Compute the url for the refresh button
    def url_for_refresh(self, /) -> str:
        return url_for('set.refresh', id=self.fields.id)

    # Compute the url for the set storage
    def url_for_storage(self, /) -> str:
        if self.fields.storage is not None:
            return url_for('storage.details', id=self.fields.storage)
        else:
            return ''
