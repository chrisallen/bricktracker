# Some stats on the database
class BrickSQLStats(object):
    # Functions
    connect: int
    commit: int
    execute: int
    executescript: int
    fetchall: int
    fetchone: int

    # Records
    fetched: int
    changed: int

    def __init__(self, /):
        self.connect = 0
        self.commit = 0
        self.execute = 0
        self.executescript = 0
        self.fetchall = 0
        self.fetchone = 0
        self.fetched = 0
        self.changed = 0

    # Print the stats
    def print(self, /) -> str:
        items: list[str] = []

        for key, value in self.__dict__.items():
            if value:
                items.append('{key}: {value}'.format(
                    key=key.capitalize(),
                    value=value,
                ))

        return ' - '.join(items)
