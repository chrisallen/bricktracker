from typing import Tuple

# Some table aliases to make it look cleaner (id: (name, icon))
ALIASES: dict[str, Tuple[str, str]] = {
    'bricktracker_minifigures': ('Bricktracker minifigures', 'group-line'),
    'bricktracker_set_checkboxes': ('Bricktracker set checkboxes', 'checkbox-line'),  # noqa: E501
    'bricktracker_set_statuses': ('Bricktracker sets status', 'checkbox-line'),
    'bricktracker_sets': ('Bricktracker sets', 'hashtag'),
    'bricktracker_wishes': ('Bricktracker wishes', 'gift-line'),
    'inventory': ('Parts', 'shapes-line'),
    'minifigures': ('Minifigures', 'group-line'),
    'minifigures_old': ('Minifigures (legacy)', 'group-line'),
    'missing': ('Missing', 'error-warning-line'),
    'rebrickable_minifigures': ('Rebrickable minifigures', 'group-line'),
    'rebrickable_sets': ('Rebrickable sets', 'hashtag'),
    'sets': ('Sets', 'hashtag'),
    'sets_old': ('Sets (legacy)', 'hashtag'),
    'wishlist': ('Wishlist', 'gift-line'),
    'wishlist_old': ('Wishlist (legacy)', 'gift-line'),
}


class BrickCounter(object):
    name: str
    table: str
    icon: str
    count: int
    legacy: bool

    def __init__(
        self,
        table: str,
        /,
        *,
        name: str | None = None,
        icon: str = 'question-line'
    ):
        self.table = table

        # Check if there is an alias
        if table in ALIASES:
            self.name = ALIASES[table][0]
            self.icon = ALIASES[table][1]
        else:
            if name is None:
                self.name = table
            else:
                self.name = name

            self.icon = icon

        self.legacy = '(legacy)' in self.name
