import json
import logging
import time
from typing import Any

from flask import current_app

from .sql import BrickSQL

logger = logging.getLogger(__name__)


# Persistent cache for sidecar responses, backed by the sidecar_set_cache table
# (migration 0028). Everything here is best-effort: if the database is missing,
# locked, or not migrated, every method degrades to "no cache" instead of
# raising, so the sidecar client keeps working even without a usable database.
class BrickSidecarCache(object):
    # Read the cache row for a ref. Returns a dict with parsed payloads and
    # timestamps, or None when there is no row / the cache is unavailable.
    @staticmethod
    def read(set_ref: str, /) -> dict[str, Any] | None:
        try:
            row = BrickSQL().fetchone(
                'sidecar/select',
                parameters={'set_ref': set_ref},
            )
        except Exception as exception:
            logger.debug('sidecar cache read failed for %s: %s', set_ref, exception)
            return None

        if row is None:
            return None

        return {
            'payload': BrickSidecarCache._loads(row['payload']),
            'price_payload': BrickSidecarCache._loads(row['price_payload']),
            'fetched_at': row['fetched_at'],
            'price_fetched_at': row['price_fetched_at'],
        }

    # Store the metadata payload (effectively permanent until refreshed).
    @staticmethod
    def write_metadata(set_ref: str, payload: dict[str, Any], /) -> None:
        BrickSidecarCache._write('sidecar/upsert_metadata', {
            'set_ref': set_ref,
            'payload': json.dumps(payload),
            'fetched_at': time.time(),
        })

    # Store the price payload (subject to the SIDECAR_PRICE_CACHE_HOURS TTL).
    @staticmethod
    def write_price(set_ref: str, payload: dict[str, Any], /) -> None:
        BrickSidecarCache._write('sidecar/upsert_price', {
            'set_ref': set_ref,
            'price_payload': json.dumps(payload),
            'price_fetched_at': time.time(),
        })

    # Tells whether a stored price timestamp is still within the configured TTL.
    @staticmethod
    def price_is_fresh(price_fetched_at: Any, /) -> bool:
        if not price_fetched_at:
            return False

        hours = int(current_app.config.get('SIDECAR_PRICE_CACHE_HOURS', 24))
        if hours <= 0:
            return False

        try:
            age = time.time() - float(price_fetched_at)
        except (TypeError, ValueError):
            return False

        return age < (hours * 3600)

    # Drop a cached row (used when invalidating).
    @staticmethod
    def invalidate(set_ref: str, /) -> None:
        BrickSidecarCache._write('sidecar/delete', {'set_ref': set_ref})

    # --- Internal -------------------------------------------------------

    @staticmethod
    def _write(query: str, parameters: dict[str, Any], /) -> None:
        try:
            BrickSQL().execute_and_commit(query, parameters=parameters)
        except Exception as exception:
            # Caching is never allowed to break a request.
            logger.debug('sidecar cache write (%s) failed: %s', query, exception)

    @staticmethod
    def _loads(value: Any) -> Any:
        if not value:
            return None
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return None
