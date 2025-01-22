from sqlite3 import Row
from typing import Any, Self

from flask import current_app, url_for

from .exceptions import DatabaseException, NotFoundException
from .instructions import BrickInstructions
from .instructions_list import BrickInstructionsList
from .minifigure_list import BrickMinifigureList
from .part_list import BrickPartList
from .rebrickable_image import RebrickableImage
from .record import BrickRecord
from .sql import BrickSQL
from .theme_list import BrickThemeList


# Lego brick set
class BrickSet(BrickRecord):
    instructions: list[BrickInstructions]
    theme_name: str

    # Queries
    select_query: str = 'set/select'
    insert_query: str = 'set/insert'

    def __init__(
        self,
        /,
        *,
        record: Row | dict[str, Any] | None = None,
    ):
        super().__init__()

        # Placeholders
        self.theme_name = ''
        self.instructions = []

        # Ingest the record if it has one
        if record is not None:
            self.ingest(record)

            # Resolve the theme
            self.resolve_theme()

            # Check for the instructions
            self.resolve_instructions()

    # Delete a set
    def delete(self, /) -> None:
        database = BrickSQL()
        parameters = self.sql_parameters()

        # Delete the set
        database.execute('set/delete/set', parameters=parameters)

        # Delete the minifigures
        database.execute(
            'minifigure/delete/all_from_set', parameters=parameters)

        # Delete the parts
        database.execute(
            'part/delete/all_from_set', parameters=parameters)

        # Delete missing parts
        database.execute('missing/delete/all_from_set', parameters=parameters)

        # Commit to the database
        database.commit()

    # Minifigures
    def minifigures(self, /) -> BrickMinifigureList:
        return BrickMinifigureList().load(self)

    # Parts
    def parts(self, /) -> BrickPartList:
        return BrickPartList().load(self)

    # Add instructions to the set
    def resolve_instructions(self, /) -> None:
        if self.fields.set_num is not None:
            self.instructions = BrickInstructionsList().get(
                self.fields.set_num
            )

    # Add a theme to the set
    def resolve_theme(self, /) -> None:
        try:
            id = self.fields.theme_id
        except Exception:
            id = 0

        theme = BrickThemeList().get(id)
        self.theme_name = theme.name

    # Return a short form of the set
    def short(self, /) -> dict[str, Any]:
        return {
            'name': self.fields.name,
            'set_img_url': self.fields.set_img_url,
            'set_num': self.fields.set_num,
        }

    # Select a specific part (with a set and an id)
    def select_specific(self, u_id: str, /) -> Self:
        # Save the parameters to the fields
        self.fields.u_id = u_id

        # Load from database
        record = self.select()

        if record is None:
            raise NotFoundException(
                'Set with ID {id} was not found in the database'.format(
                    id=self.fields.u_id,
                ),
            )

        # Ingest the record
        self.ingest(record)

        # Resolve the theme
        self.resolve_theme()

        # Check for the instructions
        self.resolve_instructions()

        return self

    # Update a checked state
    def update_checked(self, name: str, status: bool, /) -> None:
        parameters = self.sql_parameters()
        parameters['status'] = status

        # Update the checked status
        rows, _ = BrickSQL().execute_and_commit(
            'set/update_checked',
            parameters=parameters,
            name=name,
        )

        if rows != 1:
            raise DatabaseException('Could not update the status {status} for set {number}'.format(  # noqa: E501
                status=name,
                number=self.fields.set_num,
            ))

    # Self url
    def url(self, /) -> str:
        return url_for('set.details', id=self.fields.u_id)

    # Deletion url
    def url_for_delete(self, /) -> str:
        return url_for('set.delete', id=self.fields.u_id)

    # Actual deletion url
    def url_for_do_delete(self, /) -> str:
        return url_for('set.do_delete', id=self.fields.u_id)

    # Compute the url for the set image
    def url_for_image(self, /) -> str:
        if not current_app.config['USE_REMOTE_IMAGES']:
            return RebrickableImage.static_url(
                self.fields.set_num,
                'SETS_FOLDER'
            )
        else:
            return self.fields.set_img_url

    # Compute the url for the set instructions
    def url_for_instructions(self, /) -> str:
        if len(self.instructions):
            return url_for(
                'set.details',
                id=self.fields.u_id,
                open_instructions=True
            )
        else:
            return ''

    # Check minifigure collected url
    def url_for_minifigures_collected(self, /) -> str:
        return url_for('set.minifigures_collected', id=self.fields.u_id)

    # Compute the url for the rebrickable page
    def url_for_rebrickable(self, /) -> str:
        if current_app.config['REBRICKABLE_LINKS']:
            try:
                return current_app.config['REBRICKABLE_LINK_SET_PATTERN'].format(  # noqa: E501
                    number=self.fields.set_num.lower(),
                )
            except Exception:
                pass

        return ''

    # Check set checked url
    def url_for_set_checked(self, /) -> str:
        return url_for('set.set_checked', id=self.fields.u_id)

    # Check set collected url
    def url_for_set_collected(self, /) -> str:
        return url_for('set.set_collected', id=self.fields.u_id)

    # Normalize from Rebrickable
    @staticmethod
    def from_rebrickable(data: dict[str, Any], /, **_) -> dict[str, Any]:
        return {
            'set_num': data['set_num'],
            'name': data['name'],
            'year': data['year'],
            'theme_id': data['theme_id'],
            'num_parts': data['num_parts'],
            'set_img_url': data['set_img_url'],
            'set_url': data['set_url'],
            'last_modified_dt': data['last_modified_dt'],
            'mini_col': False,
            'set_col': False,
            'set_check': False,
        }
