from typing import Self

from .exceptions import ErrorException
from .metadata import BrickMetadata


# Lego set checkbox
class BrickSetCheckbox(BrickMetadata):
    kind: str = 'checkbox'
    prefix: str = 'status'

    # Set state endpoint
    set_state_endpoint: str = 'set.update_status'

    # Queries
    delete_query: str = 'checkbox/delete'
    insert_query: str = 'checkbox/insert'
    select_query: str = 'checkbox/select'
    update_field_query: str = 'checkbox/update/field'
    update_set_state_query: str = 'set/update/status'

    # Grab data from a form
    def from_form(self, form: dict[str, str], /) -> Self:
        name = form.get('name', None)
        grid = form.get('grid', None)

        if name is None or name == '':
            raise ErrorException('Checkbox name cannot be empty')

        self.fields.name = name
        self.fields.displayed_on_grid = grid == 'on'

        return self

    # Insert into database
    def insert(self, /, **_) -> None:
        super().insert(
            displayed_on_grid=self.fields.displayed_on_grid
        )
