from glob import glob
import logging
import os

from .sql_migration import BrickSQLMigration

logger = logging.getLogger(__name__)


class BrickSQLMigrationList(object):
    migrations: list[BrickSQLMigration]

    def __init__(self):
        # Load the migrations only there is none already loaded
        migrations = getattr(self, 'migrations', None)

        if migrations is None:
            logger.info('Loading SQL migrations list')

            BrickSQLMigrationList.migrations = []

            path: str = os.path.join(
                os.path.dirname(__file__),
                'sql/migrations/*.sql'
            )

            files = glob(path)

            for file in files:
                try:
                    BrickSQLMigrationList.migrations.append(
                        BrickSQLMigration(file)
                    )
                # Ignore file if error
                except Exception:
                    pass

    # Get the sorted list of pending migrations
    def pending(
        self,
        current: int,
        /
    ) -> list[BrickSQLMigration]:
        pending: list[BrickSQLMigration] = []

        for migration in self.migrations:
            if migration.is_needed(current):
                pending.append(migration)

        # Sort the list
        pending.sort(key=lambda e: e.version)

        return pending
