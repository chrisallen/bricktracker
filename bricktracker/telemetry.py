import json
import logging
import random
import time
import uuid
from typing import Any, Callable, Final
from urllib.parse import urlencode

from flask import Flask, current_app
import gevent
import requests

from .config_manager import ConfigManager
from .sidecar import BrickSidecar
from .sql import BrickSQL, close
from .statistics import BrickStatistics
from .version import __version__
from .wish_list import BrickWishList

logger = logging.getLogger(__name__)

# Self-hosted Matomo instance. Not user-configurable: every opted-in
# installation reports to this one site so the counts are actually aggregable.
MATOMO_URL: Final[str] = 'https://matomo.baerentsen.space'
MATOMO_SITE_ID: Final[int] = 6

# Short timeout: a slow/offline Matomo must never be felt by a real user.
TIMEOUT: Final[int] = 2

# Collection stats are cheap but pointless to send more than once a day.
COLLECTION_STATS_INTERVAL: Final[int] = 24 * 60 * 60

# Queued events are flushed as one Matomo Bulk Tracking request at most
# this often, per the throttle in BrickTelemetry.maybe_flush_queue().
FLUSH_INTERVAL: Final[int] = 15 * 60

# GET endpoints that count as a "page view" for the Usage category. Endpoints
# not listed here are simply never tracked. There is no default-on catch-all.
PAGEVIEW_ENDPOINTS: Final[dict[str, str]] = {
    'index.index': 'Dashboard',
    'statistics.overview': 'Statistics',
    'wish.list': 'Wishlist',
    'minifigure.list': 'Minifigures',
    'set.list': 'Sets',
    'part.list': 'Parts',
    'storage.list': 'Storage',
    'admin.admin': 'Settings',
}

# Blueprints with several GET routes that all count as the same page for
# telemetry purposes (e.g. every export format is still just "Exports").
PAGEVIEW_BLUEPRINTS: Final[dict[str, str]] = {
    'add': 'Imports',
    'admin_export': 'Exports',
}


# Best-effort anonymous telemetry client, reporting to a self-hosted Matomo
# instance. See templates/telemetry/_privacy_explainer.html for the full
# privacy explanation shown to users.
class BrickTelemetry(object):
    # Throttle cache for collection stats, mirrors BrickSidecar._health_cache.
    _last_collection_stats_at: float | None = None

    # Throttle cache for queue flushes, same shape as above.
    _last_flush_attempt_at: float | None = None

    # Lazily hydrated from TELEMETRY_QUEUE_PATH on first access this process.
    # None means "not loaded yet"; [] means "loaded, currently empty".
    _queue: list[dict[str, Any]] | None = None

    # --- Configuration helpers ------------------------------------------

    @staticmethod
    def enabled() -> bool:
        return (
            bool(current_app.config.get('TELEMETRY_ENABLED'))
            and bool(current_app.config.get('TELEMETRY_INSTALLATION_ID'))
        )

    @staticmethod
    def category_enabled(category_config_name: str, /) -> bool:
        return (
            BrickTelemetry.enabled()
            and bool(current_app.config.get(category_config_name))
        )

    # Generate the installation UUID exactly once, at boot, if telemetry is
    # enabled and no ID exists yet. Never called again afterwards: there is
    # deliberately no regenerate/reset path, so the ID (and the Matomo
    # visitor history behind it) stays stable for the life of the install.
    @staticmethod
    def generate_installation_id(app: Flask, /) -> None:
        if not app.config.get('TELEMETRY_ENABLED'):
            return

        if app.config.get('TELEMETRY_INSTALLATION_ID'):
            return

        installation_id = str(uuid.uuid4())
        app.config['TELEMETRY_INSTALLATION_ID'] = installation_id

        try:
            ConfigManager()._update_env_file(
                'BK_TELEMETRY_INSTALLATION_ID', installation_id,
            )
        except Exception as exception:
            logger.debug(
                'telemetry: failed to persist installation id: %s', exception,
            )

    # Matomo's visitor ID format: exactly 16 hex characters.
    @staticmethod
    def _visitor_id() -> str:
        installation_id = str(
            current_app.config.get('TELEMETRY_INSTALLATION_ID') or ''
        )
        return installation_id.replace('-', '')[:16]

    # --- Queue persistence -------------------------------------------------

    @staticmethod
    def _load_queue() -> list[dict[str, Any]]:
        if BrickTelemetry._queue is not None:
            return BrickTelemetry._queue

        path = current_app.config.get('TELEMETRY_QUEUE_PATH')
        queue: list[dict[str, Any]] = []

        try:
            with open(path, 'r') as queue_file:
                loaded = json.load(queue_file)
            if isinstance(loaded, list):
                queue = loaded
        except (OSError, ValueError):
            pass

        BrickTelemetry._queue = queue
        return queue

    @staticmethod
    def _save_queue() -> None:
        path = current_app.config.get('TELEMETRY_QUEUE_PATH')

        try:
            with open(path, 'w') as queue_file:
                json.dump(BrickTelemetry._queue or [], queue_file)
        except OSError as exception:
            logger.debug(
                'telemetry: failed to persist queue: %s', exception,
            )

    @staticmethod
    def _enqueue(params: dict[str, Any], /) -> None:
        BrickTelemetry._load_queue().append(params)

    # --- Background dispatch ---------------------------------------------

    # Nothing here ever runs on the request thread. The greenlet outlives
    # the request, so it needs its own real app object and its own app
    # context to talk to config, the db, etc.
    @staticmethod
    def _async(func: Callable[[], None], /) -> None:
        try:
            # current_app is a proxy that only works during a request.
            # Unwrap it now, while we still can, and hand the real object
            # to the greenlet.
            app = current_app._get_current_object()  # type: ignore[attr-defined]  # noqa: E501
        except RuntimeError:
            return

        def runner() -> None:
            with app.app_context():
                try:
                    func()
                except Exception as exception:
                    logger.debug(
                        'telemetry: background task failed: %s', exception,
                    )
                finally:
                    # Save even on failure, so whatever got queued before
                    # things broke isn't lost, and always close the db
                    # connection this greenlet opened.
                    BrickTelemetry._save_queue()
                    close()

        gevent.spawn(runner)

    # --- Public tracking API ----------------------------------------------

    @staticmethod
    def pageview_name(endpoint: str | None, /) -> str | None:
        if not endpoint:
            return None

        if endpoint in PAGEVIEW_ENDPOINTS:
            return PAGEVIEW_ENDPOINTS[endpoint]

        blueprint = endpoint.split('.', 1)[0]
        return PAGEVIEW_BLUEPRINTS.get(blueprint)

    @staticmethod
    def track_pageview(name: str, /) -> None:
        if not BrickTelemetry.category_enabled('TELEMETRY_CATEGORY_USAGE'):
            return

        BrickTelemetry._async(lambda: BrickTelemetry._send_pageview(name))

    @staticmethod
    def track_action(name: str, /) -> None:
        if not BrickTelemetry.category_enabled('TELEMETRY_CATEGORY_USAGE'):
            return

        BrickTelemetry._async(lambda: BrickTelemetry._send_action(name))

    @staticmethod
    def send_installation_info() -> None:
        if not BrickTelemetry.category_enabled(
            'TELEMETRY_CATEGORY_INSTALLATION',
        ):
            return

        BrickTelemetry._async(BrickTelemetry._send_installation_info)

    @staticmethod
    def maybe_send_collection_stats() -> None:
        if not BrickTelemetry.category_enabled(
            'TELEMETRY_CATEGORY_COLLECTION',
        ):
            return

        now = time.monotonic()
        last = BrickTelemetry._last_collection_stats_at

        if last is not None and (now - last) < COLLECTION_STATS_INTERVAL:
            return

        BrickTelemetry._last_collection_stats_at = now
        BrickTelemetry._async(BrickTelemetry._send_collection_stats)

    @staticmethod
    def maybe_flush_queue(*, force: bool = False) -> None:
        if not BrickTelemetry.enabled():
            return

        now = time.monotonic()
        last = BrickTelemetry._last_flush_attempt_at

        if not force and last is not None and (now - last) < FLUSH_INTERVAL:
            return

        BrickTelemetry._last_flush_attempt_at = now
        BrickTelemetry._async(BrickTelemetry._flush_queue)

    # --- Payload builders + senders (run inside the background greenlet) --

    @staticmethod
    def _base_params(url_suffix: str, /) -> dict[str, Any]:
        return {
            'idsite': MATOMO_SITE_ID,
            'rec': 1,
            'apiv': 1,
            'rand': random.randint(0, 1_000_000_000),
            'cid': BrickTelemetry._visitor_id(),
            'url': 'app://bricktracker/{suffix}'.format(suffix=url_suffix),
        }

    @staticmethod
    def _send_pageview(name: str, /) -> None:
        params = BrickTelemetry._base_params(name)
        params['action_name'] = name

        BrickTelemetry._enqueue(params)

    @staticmethod
    def _send_action(name: str, /) -> None:
        params = BrickTelemetry._base_params(name)
        params.update({'e_c': 'Usage', 'e_a': name})

        BrickTelemetry._enqueue(params)

    @staticmethod
    def _send_installation_info() -> None:
        version_params = BrickTelemetry._base_params('Version')
        version_params.update({
            'e_c': 'Installation', 'e_a': 'Version', 'e_n': __version__,
        })
        BrickTelemetry._enqueue(version_params)

        schema_params = BrickTelemetry._base_params('Schema')
        schema_params.update({
            'e_c': 'Installation',
            'e_a': 'Schema',
            'e_v': BrickSQL(failsafe=True).version,
        })
        BrickTelemetry._enqueue(schema_params)

        flags = {
            'SidecarEnabled': BrickSidecar.enabled(),
            'SetsServerSidePagination': bool(
                current_app.config.get('SETS_SERVER_SIDE_PAGINATION'),
            ),
            'PartsServerSidePagination': bool(
                current_app.config.get('PARTS_SERVER_SIDE_PAGINATION'),
            ),
            'MinifiguresServerSidePagination': bool(
                current_app.config.get('MINIFIGURES_SERVER_SIDE_PAGINATION'),
            ),
            'ProblemsServerSidePagination': bool(
                current_app.config.get('PROBLEMS_SERVER_SIDE_PAGINATION'),
            ),
        }

        for action, flag in flags.items():
            flag_params = BrickTelemetry._base_params(action)
            flag_params.update({
                'e_c': 'Installation', 'e_a': action, 'e_v': int(flag),
            })
            BrickTelemetry._enqueue(flag_params)

    @staticmethod
    def _send_collection_stats() -> None:
        summary = BrickStatistics().get_collection_summary()

        counts = {
            'Sets': summary['total_sets'],
            'Minifigures': summary['total_minifigures_count'],
            'Parts': summary['total_parts_count'],
            'Lots': summary['total_part_lots'],
            'MissingParts': summary['total_missing_parts'],
            'DamagedParts': summary['total_damaged_parts'],
            'Wishlist': len(BrickWishList().all()),
        }

        for action, value in counts.items():
            params = BrickTelemetry._base_params(action)
            params.update({'e_c': 'Collection', 'e_a': action, 'e_v': value})
            BrickTelemetry._enqueue(params)

    @staticmethod
    def _bulk_payload(queue: list[dict[str, Any]], /) -> dict[str, Any]:
        return {
            'requests': [
                '?{qs}'.format(qs=urlencode(params)) for params in queue
            ],
        }

    @staticmethod
    def _send_bulk(queue: list[dict[str, Any]], /) -> bool:
        try:
            response = requests.post(
                '{base}/matomo.php'.format(base=MATOMO_URL),
                json=BrickTelemetry._bulk_payload(queue),
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            return True
        except Exception as exception:
            logger.debug('telemetry: bulk send failed: %s', exception)
            return False

    @staticmethod
    def _flush_queue() -> None:
        queue = BrickTelemetry._load_queue()

        if queue and BrickTelemetry._send_bulk(queue):
            BrickTelemetry._queue = []


if __name__ == '__main__':
    sample_payloads = [
        {'action_name': 'Dashboard'},
        {'e_c': 'Installation', 'e_a': 'Version', 'e_n': '1.5.0'},
        {'e_c': 'Installation', 'e_a': 'Schema', 'e_v': 30},
        {'e_c': 'Collection', 'e_a': 'Sets', 'e_v': 42},
        {'e_c': 'Collection', 'e_a': 'Wishlist', 'e_v': 3},
        {'e_c': 'Usage', 'e_a': 'AddSet'},
    ]

    for payload in sample_payloads:
        for key, value in payload.items():
            assert key in (
                'action_name', 'e_c', 'e_a', 'e_n', 'e_v',
            ), 'unexpected telemetry param key: {key}'.format(key=key)
            assert isinstance(value, (str, int)), (
                'unexpected telemetry param type for {key}'.format(key=key)
            )

    print('telemetry payload self-check OK ({count} samples)'.format(
        count=len(sample_payloads),
    ))

    empty_payload = BrickTelemetry._bulk_payload([])
    assert empty_payload == {'requests': []}, empty_payload

    bulk_payload = BrickTelemetry._bulk_payload(sample_payloads)
    assert len(bulk_payload['requests']) == len(sample_payloads)

    for request_qs, payload in zip(bulk_payload['requests'], sample_payloads):
        assert request_qs.startswith('?'), request_qs
        for key, value in payload.items():
            assert '{key}={value}'.format(key=key, value=value) in request_qs, (
                request_qs
            )

    print('telemetry bulk payload self-check OK ({count} samples)'.format(
        count=len(bulk_payload['requests']),
    ))
