from importlib import import_module
import logging
import os
import sqlite3
from typing import Any, Final, Tuple

from flask import current_app, g
from jinja2 import Environment, FileSystemLoader
from werkzeug.datastructures import FileStorage

from .exceptions import DatabaseException
from .sql_counter import BrickCounter
from .sql_migration_list import BrickSQLMigrationList
from .sql_stats import BrickSQLStats
from .version import __database_version__

logger = logging.getLogger(__name__)

G_CONNECTION: Final[str] = 'database_connection'
G_ENVIRONMENT: Final[str] = 'database_environment'
G_DEFER: Final[str] = 'database_defer'
G_STATS: Final[str] = 'database_stats'


# SQLite3 client with our extra features
class BrickSQL(object):
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor
    stats: BrickSQLStats
    version: int

    def __init__(self, /, *, failsafe: bool = False):
        # Instantiate the database connection in the Flask
        # application context so that it can be used by all
        # requests without re-opening connections
        connection = getattr(g, G_CONNECTION, None)

        # Grab the existing connection if it exists
        if connection is not None:
            self.connection = connection
            self.stats = getattr(g, G_STATS, BrickSQLStats())

            # Grab a cursor
            self.cursor = self.connection.cursor()
        else:
            # Instantiate the stats
            self.stats = BrickSQLStats()

            # Stats: connect
            self.stats.connect += 1

            logger.debug('SQLite3: connect')
            self.connection = sqlite3.connect(
                current_app.config['DATABASE_PATH']
            )

            # Setup the row factory to get pseudo-dicts rather than tuples
            self.connection.row_factory = sqlite3.Row

            # Grab a cursor
            self.cursor = self.connection.cursor()

            # Grab the version and check
            try:
                version = self.fetchone('schema/get_version')

                if version is None:
                    raise Exception('version is None')

                self.version = version[0]
            except Exception as e:
                self.version = 0

                raise DatabaseException('Could not get the database version: {error}'.format(  # noqa: E501
                    error=str(e)
                ))

            if self.upgrade_too_far():
                raise DatabaseException('Your database version ({version}) is too far ahead for this version of the application. Expected at most {required}'.format(  # noqa: E501
                    version=self.version,
                    required=__database_version__,
                ))

            # Debug: Attach the debugger
            # Uncomment manually because this is ultra verbose
            # self.connection.set_trace_callback(print)

            # Save the connection globally for later use
            setattr(g, G_CONNECTION, self.connection)
            setattr(g, G_STATS, self.stats)

            if not failsafe:
                if self.upgrade_needed():
                    raise DatabaseException('Your database need to be upgraded from version {version} to version {required}'.format(  # noqa: E501
                        version=self.version,
                        required=__database_version__,
                    ))

    # Clear the defer stack
    def clear_defer(self, /) -> None:
        setattr(g, G_DEFER, [])

    # Shorthand to commit
    def commit(self, /) -> None:
        # Stats: commit
        self.stats.commit += 1

        # Process the defered stack
        for item in self.get_defer():
            self.raw_execute(item[0], item[1])

        self.clear_defer()

        logger.debug('SQLite3: commit')
        return self.connection.commit()

    # Count the database records
    def count_records(self) -> list[BrickCounter]:
        counters: list[BrickCounter] = []

        # Get all tables
        for table in self.fetchall('schema/tables'):
            counter = BrickCounter(table['name'])

            # Failsafe this one
            try:
                record = self.fetchone('schema/count', table=counter.table)

                if record is not None:
                    counter.count = record['count']
            except Exception:
                pass

            counters.append(counter)

        return counters

    # Defer a call to execute
    def defer(self, query: str, parameters: dict[str, Any], /):
        defer = self.get_defer()

        logger.debug('SQLite3: defer execute')

        # Add the query and parameters to the defer stack
        defer.append((query, parameters))

        # Save the defer stack
        setattr(g, G_DEFER, defer)

    # Shorthand to execute, returning number of affected rows
    def execute(
        self,
        query: str,
        /,
        *,
        parameters: dict[str, Any] = {},
        defer: bool = False,
        **context: Any,
    ) -> Tuple[int, str]:
        # Stats: execute
        self.stats.execute += 1

        # Load the query
        query = self.load_query(query, **context)

        # Defer
        if defer:
            self.defer(query, parameters)

            return -1, query
        else:
            result = self.raw_execute(query, parameters)

            # Stats: changed
            if result.rowcount > 0:
                self.stats.changed += result.rowcount

            return result.rowcount, query

    # Shorthand to executescript
    def executescript(self, query: str, /, **context: Any) -> None:
        # Load the query
        query = self.load_query(query, **context)

        # Stats: executescript
        self.stats.executescript += 1

        logger.debug('SQLite3: executescript')
        self.cursor.executescript(query)

    # Shorthand to execute and commit
    def execute_and_commit(
        self,
        query: str,
        /,
        *,
        parameters: dict[str, Any] = {},
        **context: Any,
    ) -> Tuple[int, str]:
        rows, query = self.execute(query, parameters=parameters, **context)
        self.commit()

        return rows, query

    # Shorthand to execute and fetchall
    def fetchall(
        self,
        query: str,
        /,
        *,
        parameters: dict[str, Any] = {},
        **context: Any,
    ) -> list[sqlite3.Row]:
        _, query = self.execute(query, parameters=parameters, **context)

        # Stats: fetchall
        self.stats.fetchall += 1

        logger.debug('SQLite3: fetchall')
        records = self.cursor.fetchall()

        # Stats: fetched
        self.stats.fetched += len(records)

        return records

    # Shorthand to execute and fetchone
    def fetchone(
        self,
        query: str,
        /,
        *,
        parameters: dict[str, Any] = {},
        **context: Any,
    ) -> sqlite3.Row | None:
        _, query = self.execute(query, parameters=parameters, **context)

        # Stats: fetchone
        self.stats.fetchone += 1

        logger.debug('SQLite3: fetchone')
        record = self.cursor.fetchone()

        # Stats: fetched
        if record is not None:
            self.stats.fetched += len(record)

        return record

    # Grab the defer stack
    def get_defer(self, /) -> list[Tuple[str, dict[str, Any]]]:
        defer: list[Tuple[str, dict[str, Any]]] = getattr(g, G_DEFER, [])

        return defer

    # Load a query by name
    def load_query(self, name: str, /, **context: Any) -> str:
        # Grab the existing environment if it exists
        environment = getattr(g, G_ENVIRONMENT, None)

        # Instantiate Jinja environment for SQL files
        if environment is None:
            logger.debug('SQLite3: instantiating the Jinja loader')
            environment = Environment(
                loader=FileSystemLoader(
                    os.path.join(os.path.dirname(__file__), 'sql/')
                )
            )

            # Save the environment globally for later use
            setattr(g, G_ENVIRONMENT, environment)

        # Grab the template
        logger.debug('SQLite3: loading {name} (context: {context})'.format(
            name=name,
            context=context,
        ))
        template = environment.get_template('{name}.sql'.format(
            name=name,
        ))

        return template.render(**context)

    # Raw execute the query without any options
    def raw_execute(
        self,
        query: str,
        parameters: dict[str, Any],
        /
    ) -> sqlite3.Cursor:
        logger.debug('SQLite3: execute: {query}'.format(
            query=BrickSQL.clean_query(query)
        ))

        return self.cursor.execute(query, parameters)

    # Upgrade the database
    def upgrade(self) -> None:
        if self.upgrade_needed():
            for pending in BrickSQLMigrationList().pending(self.version):
                logger.info('Applying migration {version}'.format(
                    version=pending.version)
                )

                # Load context from the migrations if it exists
                # It looks for a file in migrations/ named after the SQL file
                # and containing one function named migration_xxxx, also named
                # after the SQL file, returning a context dict.
                #
                # For instance:
                # - sql/migrations/0007.sql
                # - migrations/0007.py
                #    - def migration_0007(BrickSQL) -> dict[str, Any]
                try:
                    module = import_module(
                        '.migrations.{name}'.format(
                            name=pending.name
                        ),
                        package='bricktracker'
                    )
                except Exception:
                    module = None

                # If a module has been loaded, we need to fail if an error
                # occured while executing the migration function
                if module is not None:
                    function = getattr(module, 'migration_{name}'.format(
                        name=pending.name
                    ))

                    context: dict[str, Any] = function(self)
                else:
                    context: dict[str, Any] = {}

                self.executescript(pending.get_query(), **context)
                self.execute('schema/set_version', version=pending.version)

    # Tells whether the database needs upgrade
    def upgrade_needed(self) -> bool:
        return self.version < __database_version__

    # Tells whether the database is too far
    def upgrade_too_far(self) -> bool:
        return self.version > __database_version__

    # Clean the query for debugging
    @staticmethod
    def clean_query(query: str, /) -> str:
        cleaned: list[str] = []

        for line in query.splitlines():
            # Keep the non-comment side
            line, sep, comment = line.partition('--')

            # Clean the non-comment side
            line = line.strip()

            if line:
                cleaned.append(line)

        return ' '.join(cleaned)

    # Delete the database
    @staticmethod
    def delete() -> None:
        os.remove(current_app.config['DATABASE_PATH'])

        # Info
        logger.info('The database has been deleted')

    # Drop the database
    @staticmethod
    def drop() -> None:
        BrickSQL().executescript('schema/drop')

        # Info
        logger.info('The database has been dropped')

    # Replace the database with a new file
    @staticmethod
    def upload(file: FileStorage, /) -> None:
        file.save(current_app.config['DATABASE_PATH'])

        # Info
        logger.info('The database has been imported using file {file}'.format(
            file=file.filename
        ))


# Close all existing SQLite3 connections
def close() -> None:
    connection: sqlite3.Connection | None = getattr(g, G_CONNECTION, None)

    if connection is not None:
        logger.debug('SQLite3: close')
        connection.close()

        # Remove the database from the context
        delattr(g, G_CONNECTION)
