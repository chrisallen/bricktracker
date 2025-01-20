import logging
import os
import sqlite3
from typing import Any, Final, Tuple

from .sql_stats import BrickSQLStats

from flask import current_app, g
from jinja2 import Environment, FileSystemLoader
from werkzeug.datastructures import FileStorage

from .sql_counter import BrickCounter

logger = logging.getLogger(__name__)

COUNTERS: Final[list[BrickCounter]] = [
    BrickCounter('Sets', 'sets', icon='hashtag'),
    BrickCounter('Minifigures', 'minifigures', icon='group-line'),
    BrickCounter('Parts', 'inventory', icon='shapes-line'),
    BrickCounter('Missing', 'missing', icon='error-warning-line'),
]


# SQLite3 client with our extra features
class BrickSQL(object):
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor
    stats: BrickSQLStats

    def __init__(self, /):
        # Instantiate the database connection in the Flask
        # application context so that it can be used by all
        # requests without re-opening connections
        database = getattr(g, 'database', None)

        # Grab the existing connection if it exists
        if database is not None:
            self.connection = database
            self.stats = getattr(g, 'database_stats', BrickSQLStats())
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

            # Debug: Attach the debugger
            # Uncomment manually because this is ultra verbose
            # self.connection.set_trace_callback(print)

            # Save the connection globally for later use
            g.database = self.connection
            g.database_stats = self.stats

        # Grab a cursor
        self.cursor = self.connection.cursor()

    # Clear the defer stack
    def clear_defer(self, /) -> None:
        g.database_defer = []

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
        for counter in COUNTERS:
            record = self.fetchone('schema/count', table=counter.table)

            if record is not None:
                counter.count = record['count']

        return COUNTERS

    # Defer a call to execute
    def defer(self, query: str, parameters: dict[str, Any], /):
        defer = self.get_defer()

        logger.debug('SQLite3: defer execute')

        # Add the query and parameters to the defer stack
        defer.append((query, parameters))

        # Save the defer stack
        g.database_defer = defer

    # Shorthand to execute, returning number of affected rows
    def execute(
        self,
        query: str,
        /,
        parameters: dict[str, Any] = {},
        defer: bool = False,
        **context,
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
    def executescript(self, query: str, /, **context) -> None:
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
        parameters: dict[str, Any] = {},
        **context,
    ) -> Tuple[int, str]:
        rows, query = self.execute(query, parameters=parameters, **context)
        self.commit()

        return rows, query

    # Shorthand to execute and fetchall
    def fetchall(
        self,
        query: str,
        /,
        parameters: dict[str, Any] = {},
        **context,
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
        parameters: dict[str, Any] = {},
        **context,
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
        defer: list[Tuple[str, dict[str, Any]]] = getattr(
            g,
            'database_defer',
            []
        )

        return defer

    # Load a query by name
    def load_query(self, name: str, /, **context) -> str:
        # Grab the existing environment if it exists
        environment = getattr(g, 'database_loader', None)

        # Instantiate Jinja environment for SQL files
        if environment is None:
            environment = Environment(
                loader=FileSystemLoader(
                    os.path.join(os.path.dirname(__file__), 'sql/')
                )
            )

            # Save the environment globally for later use
            g.database_environment = environment

        # Grab the template
        logger.debug('SQLite: loading {name} (context: {context})'.format(
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
        parameters: dict[str, Any]
    ) -> sqlite3.Cursor:
        logger.debug('SQLite3: execute: {query}'.format(
            query=BrickSQL.clean_query(query)
        ))

        return self.cursor.execute(query, parameters)

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

    # Initialize the database
    @staticmethod
    def initialize() -> None:
        BrickSQL().executescript('migrations/init')

        # Info
        logger.info('The database has been initialized')

    # Check if the database is initialized
    @staticmethod
    def is_init() -> bool:
        return BrickSQL().fetchone('schema/is_init') is not None

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
    database: sqlite3.Connection | None = getattr(g, 'database', None)

    if database is not None:
        logger.debug('SQLite3: close')
        database.close()

        # Remove the database from the context
        delattr(g, 'database')
