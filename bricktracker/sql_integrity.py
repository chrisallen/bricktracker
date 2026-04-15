import logging

from .sql import BrickSQL

logger = logging.getLogger(__name__)


class BrickIntegrityIssue(object):
    issue_type: str
    count: int
    description: str

    def __init__(self, issue_type: str, count: int, description: str, /):
        self.issue_type = issue_type
        self.count = count
        self.description = description


class BrickOrphanedSet(object):
    set: str
    id: str
    description: str | None
    storage: str | None
    purchase_date: float | None
    purchase_location: str | None
    purchase_price: float | None

    def __init__(
        self,
        set: str,
        id: str,
        description: str | None,
        storage: str | None,
        purchase_date: float | None,
        purchase_location: str | None,
        purchase_price: float | None,
        /
    ):
        self.set = set
        self.id = id
        self.description = description
        self.storage = storage
        self.purchase_date = purchase_date
        self.purchase_location = purchase_location
        self.purchase_price = purchase_price


class BrickOrphanedPart(object):
    id: str
    part: str
    color: int
    quantity: int
    spare: bool
    missing: int
    damaged: int
    set_number: str | None

    def __init__(
        self,
        id: str,
        part: str,
        color: int,
        quantity: int,
        spare: bool,
        missing: int,
        damaged: int,
        set_number: str | None,
        /
    ):
        self.id = id
        self.part = part
        self.color = color
        self.quantity = quantity
        self.spare = spare
        self.missing = missing
        self.damaged = damaged
        self.set_number = set_number


class BrickPartMissingSet(object):
    id: str
    part: str
    color: int
    quantity: int
    spare: bool
    missing: int
    damaged: int

    def __init__(
        self,
        id: str,
        part: str,
        color: int,
        quantity: int,
        spare: bool,
        missing: int,
        damaged: int,
        /
    ):
        self.id = id
        self.part = part
        self.color = color
        self.quantity = quantity
        self.spare = spare
        self.missing = missing
        self.damaged = damaged


class BrickIntegrityCheck(object):
    def check_summary(self, /) -> list[BrickIntegrityIssue]:
        sql = BrickSQL()
        results = sql.fetchall('schema/integrity_check_summary')

        issues: list[BrickIntegrityIssue] = []
        for row in results:
            issues.append(BrickIntegrityIssue(
                row['issue_type'],
                row['count'],
                row['description']
            ))

        return issues

    def get_orphaned_sets(self, /) -> list[BrickOrphanedSet]:
        sql = BrickSQL()
        results = sql.fetchall('schema/integrity_orphaned_sets')

        sets: list[BrickOrphanedSet] = []
        for row in results:
            sets.append(BrickOrphanedSet(
                row['set'],
                row['id'],
                row['description'],
                row['storage'],
                row['purchase_date'],
                row['purchase_location'],
                row['purchase_price']
            ))

        return sets

    def get_orphaned_parts(self, /) -> list[BrickOrphanedPart]:
        sql = BrickSQL()
        results = sql.fetchall('schema/integrity_orphaned_parts')

        parts: list[BrickOrphanedPart] = []
        for row in results:
            parts.append(BrickOrphanedPart(
                row['id'],
                row['part'],
                row['color'],
                row['quantity'],
                row['spare'],
                row['missing'],
                row['damaged'],
                row['set_number']
            ))

        return parts

    def get_parts_missing_set(self, /) -> list[BrickPartMissingSet]:
        sql = BrickSQL()
        results = sql.fetchall('schema/integrity_parts_missing_set')

        parts: list[BrickPartMissingSet] = []
        for row in results:
            parts.append(BrickPartMissingSet(
                row['id'],
                row['part'],
                row['color'],
                row['quantity'],
                row['spare'],
                row['missing'],
                row['damaged']
            ))

        return parts

    def cleanup_orphaned_sets(self, /) -> int:
        sql = BrickSQL()
        orphaned = self.get_orphaned_sets()
        count = len(orphaned)

        if count > 0:
            sql.executescript('schema/integrity_delete_parts_for_orphaned_sets')
            sql.executescript('schema/integrity_delete_minifigures_for_orphaned_sets')
            sql.executescript('schema/integrity_delete_tags_for_orphaned_sets')
            sql.executescript('schema/integrity_delete_owners_for_orphaned_sets')
            sql.executescript('schema/integrity_delete_statuses_for_orphaned_sets')
            sql.executescript('schema/integrity_delete_orphaned_sets')
            sql.commit()
            logger.info(f'Deleted {count} orphaned set(s)')

        return count

    def cleanup_orphaned_parts(self, /) -> int:
        sql = BrickSQL()
        orphaned = self.get_orphaned_parts()
        count = len(orphaned)

        if count > 0:
            sql.executescript('schema/integrity_delete_orphaned_parts')
            sql.commit()
            logger.info(f'Deleted {count} orphaned part(s)')

        return count

    def cleanup_parts_missing_set(self, /) -> int:
        sql = BrickSQL()
        orphaned = self.get_parts_missing_set()
        count = len(orphaned)

        if count > 0:
            sql.executescript('schema/integrity_delete_parts_missing_set')
            sql.commit()
            logger.info(f'Deleted {count} part(s) with missing set references')

        return count

    def cleanup_all(self, /) -> dict[str, int]:
        orphaned_parts = self.cleanup_orphaned_parts()
        parts_missing_set = self.cleanup_parts_missing_set()
        orphaned_sets = self.cleanup_orphaned_sets()

        counts = {
            'orphaned_parts': orphaned_parts,
            'parts_missing_set': parts_missing_set,
            'orphaned_sets': orphaned_sets
        }

        total = sum(counts.values())
        logger.info(f'Integrity cleanup complete: {total} total records removed')

        return counts

    def optimize_database(self, /) -> None:
        sql = BrickSQL()
        sql.executescript('schema/optimize')
        sql.commit()

        sql.connection.execute('VACUUM')
        logger.info('Database optimization complete')
