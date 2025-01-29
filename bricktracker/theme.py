# Lego set theme
class BrickTheme(object):
    id: str
    name: str
    parent: str | None

    def __init__(self, id: str, name: str, parent: str | None = None, /):
        self.id = id
        self.name = name

        if parent is not None and parent != '':
            self.parent = parent
        else:
            self.parent = None
