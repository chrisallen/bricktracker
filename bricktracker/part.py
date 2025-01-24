import os
from sqlite3 import Row
from typing import Any, Self, TYPE_CHECKING
from urllib.parse import urlparse

from flask import current_app, url_for

from .exceptions import DatabaseException, ErrorException, NotFoundException
from .rebrickable_image import RebrickableImage
from .record import BrickRecord
from .sql import BrickSQL
if TYPE_CHECKING:
    from .minifigure import BrickMinifigure
    from .set import BrickSet


# Lego set or minifig part
class BrickPart(BrickRecord):
    brickset: 'BrickSet | None'
    minifigure: 'BrickMinifigure | None'

    # Queries
    insert_query: str = 'part/insert'
    generic_query: str = 'part/select/generic'
    select_query: str = 'part/select/specific'

    def __init__(
        self,
        /,
        *,
        brickset: 'BrickSet | None' = None,
        minifigure: 'BrickMinifigure | None' = None,
        record: Row | dict[str, Any] | None = None,
    ):
        super().__init__()

        # Save the brickset and minifigure
        self.brickset = brickset
        self.minifigure = minifigure

        # Ingest the record if it has one
        if record is not None:
            self.ingest(record)

    # Delete missing part
    def delete_missing(self, /) -> None:
        BrickSQL().execute_and_commit(
            'missing/delete/from_set',
            parameters=self.sql_parameters()
        )

    # Set missing part
    def set_missing(self, quantity: int, /) -> None:
        parameters = self.sql_parameters()
        parameters['quantity'] = quantity

        # Can't use UPSERT because the database has no keys
        # Try to update
        database = BrickSQL()
        rows, _ = database.execute(
            'missing/update/from_set',
            parameters=parameters,
        )

        # Insert if no row has been affected
        if not rows:
            rows, _ = database.execute(
                'missing/insert',
                parameters=parameters,
            )

            if rows != 1:
                raise DatabaseException(
                    'Could not update the missing quantity for part {id}'.format(  # noqa: E501
                        id=self.fields.id
                    )
                )

        database.commit()

    # Select a generic part
    def select_generic(
        self,
        part_num: str,
        color_id: int,
        /,
        *,
        element_id: int | None = None
    ) -> Self:
        # Save the parameters to the fields
        self.fields.part_num = part_num
        self.fields.color_id = color_id
        self.fields.element_id = element_id

        if not self.select(override_query=self.generic_query):
            raise NotFoundException(
                'Part with number {number}, color ID {color} and element ID {element} was not found in the database'.format(  # noqa: E501
                    number=self.fields.part_num,
                    color=self.fields.color_id,
                    element=self.fields.element_id,
                ),
            )

        return self

    # Select a specific part (with a set and an id, and option. a minifigure)
    def select_specific(
        self,
        brickset: 'BrickSet',
        id: str,
        /,
        *,
        minifigure: 'BrickMinifigure | None' = None,
    ) -> Self:
        # Save the parameters to the fields
        self.brickset = brickset
        self.minifigure = minifigure
        self.fields.id = id

        if not self.select():
            raise NotFoundException(
                'Part with ID {id} from set {set} was not found in the database'.format(  # noqa: E501
                    id=self.fields.id,
                    set=self.brickset.fields.set,
                ),
            )

        return self

    # Return a dict with common SQL parameters for a part
    def sql_parameters(self, /) -> dict[str, Any]:
        parameters = super().sql_parameters()

        # Supplement from the brickset
        if 'u_id' not in parameters and self.brickset is not None:
            parameters['u_id'] = self.brickset.fields.id

        if 'set_num' not in parameters:
            if self.minifigure is not None:
                parameters['set_num'] = self.minifigure.fields.fig_num

            elif self.brickset is not None:
                parameters['set_num'] = self.brickset.fields.set

        return parameters

    # Update the missing part
    def update_missing(self, missing: Any, /) -> None:
        # If empty, delete it
        if missing == '':
            self.delete_missing()

        else:
            # Try to understand it as a number
            try:
                missing = int(missing)
            except Exception:
                raise ErrorException('"{missing}" is not a valid integer'.format(  # noqa: E501
                    missing=missing
                ))

            # If 0, delete it
            if missing == 0:
                self.delete_missing()

            else:
                # If negative, it's an error
                if missing < 0:
                    raise ErrorException('Cannot set a negative missing value')

                # Otherwise upsert it
                # Not checking if it is too much, you do you
                self.set_missing(missing)

    # Self url
    def url(self, /) -> str:
        return url_for(
            'part.details',
            number=self.fields.part_num,
            color=self.fields.color_id,
            element=self.fields.element_id,
        )

    # Compute the url for the bricklink page
    def url_for_bricklink(self, /) -> str:
        if current_app.config['BRICKLINK_LINKS']:
            try:
                return current_app.config['BRICKLINK_LINK_PART_PATTERN'].format(  # noqa: E501
                    number=self.fields.part_num,
                )
            except Exception:
                pass

        return ''

    # Compute the url for the part image
    def url_for_image(self, /) -> str:
        if not current_app.config['USE_REMOTE_IMAGES']:
            if self.fields.part_img_url is None:
                file = RebrickableImage.nil_name()
            else:
                file = self.fields.part_img_url_id

            return RebrickableImage.static_url(file, 'PARTS_FOLDER')
        else:
            if self.fields.part_img_url is None:
                return current_app.config['REBRICKABLE_IMAGE_NIL']
            else:
                return self.fields.part_img_url

    # Compute the url for missing part
    def url_for_missing(self, /) -> str:
        # Different URL for a minifigure part
        if self.minifigure is not None:
            return url_for(
                'set.missing_minifigure_part',
                id=self.fields.u_id,
                minifigure_id=self.minifigure.fields.fig_num,
                part_id=self.fields.id,
            )

        return url_for(
            'set.missing_part',
            id=self.fields.u_id,
            part_id=self.fields.id
        )

    # Compute the url for the rebrickable page
    def url_for_rebrickable(self, /) -> str:
        if current_app.config['REBRICKABLE_LINKS']:
            try:
                return current_app.config['REBRICKABLE_LINK_PART_PATTERN'].format(  # noqa: E501
                    number=self.fields.part_num,
                    color=self.fields.color_id,
                )
            except Exception:
                pass

        return ''

    # Normalize from Rebrickable
    @staticmethod
    def from_rebrickable(
        data: dict[str, Any],
        /,
        *,
        brickset: 'BrickSet | None' = None,
        minifigure: 'BrickMinifigure | None' = None,
        **_,
    ) -> dict[str, Any]:
        record = {
            'set_num': data['set_num'],
            'id': data['id'],
            'part_num': data['part']['part_num'],
            'name': data['part']['name'],
            'part_img_url': data['part']['part_img_url'],
            'part_img_url_id': None,
            'color_id': data['color']['id'],
            'color_name': data['color']['name'],
            'quantity': data['quantity'],
            'is_spare': data['is_spare'],
            'element_id': data['element_id'],
        }

        if brickset is not None:
            record['u_id'] = brickset.fields.id

        if minifigure is not None:
            record['set_num'] = data['fig_num']

        # Extract the file name
        if data['part']['part_img_url'] is not None:
            part_img_url_file = os.path.basename(
                urlparse(data['part']['part_img_url']).path
            )

            part_img_url_id, _ = os.path.splitext(part_img_url_file)

            if part_img_url_id is not None or part_img_url_id != '':
                record['part_img_url_id'] = part_img_url_id

        return record
