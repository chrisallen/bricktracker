# Lego set theme
class BrickTheme(object):
    id: int
    name: str
    parent: int | None

    def __init__(self, id: str | int, name: str, parent: str | None = None, /):
        self.id = int(id)
        self.name = name

        if parent is not None and parent != '':
            self.parent = int(parent)
        else:
            self.parent = None
