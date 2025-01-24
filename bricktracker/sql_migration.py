import os

from .version import __database_version__


class BrickSQLMigration(object):
    description: str | None
    name: str
    file: str
    version: int

    # Description marker
    description_marker: str = '-- description:'

    def __init__(self, file: str):
        self.file = file
        self.name, _ = os.path.splitext(os.path.basename(self.file))
        self.version = int(self.name)

        self.description = None

    # Read the description from the migration file if it exists
    def get_description(self) -> str:
        if self.description is None:
            self.description = ''

            # First line or ignored
            with open(self.file, 'r') as file:
                line = file.readline()

                # Extract a description (only the first one)
                if line.startswith(self.description_marker):
                    self.description = line.strip()[
                        len(self.description_marker):
                    ]

        return self.description

    # Tells whether the migration is need
    def is_needed(self, current: int, /):
        return self.version > current and self.version <= __database_version__

    # Query name for the SQL loader
    def get_query(self) -> str:
        relative, _ = os.path.splitext(
            os.path.relpath(self.file, os.path.join(
                os.path.dirname(__file__),
                'sql/'
            ))
        )

        return relative
