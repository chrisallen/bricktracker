from typing import Any, Final

from flask import Flask

# Navbar map:
# - e: url endpoint (str)
# - t: title (str)
# - i: icon (str, optional=None)
# - f: flag name (str, optional=None)
NAVBAR: Final[list[dict[str, Any]]] = [
    {'e': 'set.list', 't': 'Sets', 'i': 'grid-line', 'f': 'HIDE_ALL_SETS'},  # noqa: E501
    {'e': 'add.add', 't': 'Add', 'i': 'add-circle-line', 'f': 'HIDE_ADD_SET'},  # noqa: E501
    {'e': 'part.list', 't': 'Parts', 'i': 'shapes-line', 'f': 'HIDE_ALL_PARTS'},  # noqa: E501
    {'e': 'part.problem', 't': 'Problems', 'i': 'error-warning-line', 'f': 'HIDE_ALL_PROBLEMS_PARTS'},  # noqa: E501
    {'e': 'minifigure.list', 't': 'Minifigures', 'i': 'group-line', 'f': 'HIDE_ALL_MINIFIGURES'},  # noqa: E501
    {'e': 'instructions.list', 't': 'Instructions', 'i': 'file-line', 'f': 'HIDE_ALL_INSTRUCTIONS'},  # noqa: E501
    {'e': 'storage.list', 't': 'Storages', 'i': 'archive-2-line', 'f': 'HIDE_ALL_STORAGES'},  # noqa: E501
    {'e': 'wish.list', 't': 'Wishlist', 'i': 'gift-line', 'f': 'HIDE_WISHES'},
    {'e': 'admin.admin', 't': 'Admin', 'i': 'settings-4-line', 'f': 'HIDE_ADMIN'},  # noqa: E501
]


# Navbar configuration
class Navbar(object):
    # Navbar item
    class NavbarItem(object):
        endpoint: str
        title: str
        icon: str | None
        flag: str | None

        def __init__(
            self,
            *,
            e: str,
            t: str,
            i: str | None = None,
            f: str | None = None,
        ):
            self.endpoint = e
            self.title = t
            self.icon = i
            self.flag = f

    # Load configuration
    def __init__(self, app: Flask, /):
        # Navbar storage
        app.config['_NAVBAR'] = []

        # Process all configuration items
        for item in NAVBAR:
            app.config['_NAVBAR'].append(self.NavbarItem(**item))
