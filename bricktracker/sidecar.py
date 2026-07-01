import json
import logging
import os
import time
from typing import Any, Final

from flask import current_app
import requests

logger = logging.getLogger(__name__)

# The four LEGO.com retail price regions the sidecar exposes. The sidecar
# returns each of these as a JSON *string* (not a nested object), so we parse
# them eagerly in get_set().
RETAIL_REGIONS: Final[list[str]] = ['US', 'UK', 'CA', 'DE']

# Currency code per retail region, used to label MSRP.
REGION_CURRENCY: Final[dict[str, str]] = {
    'US': 'USD',
    'UK': 'GBP',
    'CA': 'CAD',
    'DE': 'EUR',
}

# Maps a currency *symbol* (as a user might set BK_PURCHASE_CURRENCY) to the ISO
# code(s) it can stand for, so '$' is treated as the same currency as 'USD' and
# 'kr' as 'DKK'. Symbols are inherently ambiguous (several currencies share one),
# so we map to a set and treat two values as the same currency when their code
# sets overlap. Keys are normalized (lowercased, trailing dots stripped).
CURRENCY_SYMBOLS: Final[dict[str, set[str]]] = {
    '$': {'USD', 'CAD', 'AUD', 'NZD', 'HKD', 'SGD', 'MXN', 'BRL'},
    'us$': {'USD'},
    'ca$': {'CAD'},
    'c$': {'CAD'},
    'a$': {'AUD'},
    'nz$': {'NZD'},
    '€': {'EUR'},
    '£': {'GBP'},
    '¥': {'JPY', 'CNY'},
    '￥': {'JPY', 'CNY'},
    'kr': {'DKK', 'SEK', 'NOK', 'ISK'},
    'zł': {'PLN'},
    '₽': {'RUB'},
    '₹': {'INR'},
    'r$': {'BRL'},
    '₩': {'KRW'},
    '฿': {'THB'},
    '₪': {'ILS'},
    'chf': {'CHF'},
    'fr': {'CHF'},
}

# Valid BrickLink image types served by the sidecar image proxy.
IMAGE_TYPES: Final[list[str]] = [
    'box', 'box_large',
    'set', 'set_large',
    'instruction', 'instruction_large',
]

# How long (seconds) to trust a cached /health result so the UI never blocks
# on a dead sidecar.
HEALTH_CACHE_TTL: Final[int] = 30


# Best-effort client for the brickset-sidecar (BrickData) container.
#
# Design rule: a missing or broken sidecar must NEVER break an existing page.
# Every public method returns None / False on any failure and logs at debug.
# Nothing in here is allowed to raise into a request handler. Guard call sites
# with BrickSidecar.enabled().
class BrickSidecar(object):
    # Cache for the health probe: (checked_at, healthy)
    _health_cache: tuple[float, bool] | None = None

    # --- Configuration helpers ------------------------------------------

    # Normalized base URL (no trailing slash), or '' when unset.
    @staticmethod
    def base_url() -> str:
        return str(current_app.config.get('SIDECAR_URL', '') or '').rstrip('/')

    # True only when a sidecar URL is configured (the feature toggle).
    @staticmethod
    def enabled() -> bool:
        return BrickSidecar.base_url() != ''

    @staticmethod
    def timeout() -> int:
        return int(current_app.config.get('SIDECAR_TIMEOUT', 5))

    # --- Low level ------------------------------------------------------

    # Perform a GET and return the parsed JSON, or None on any failure.
    @staticmethod
    def _get_json(path: str, /, *, params: dict[str, Any] | None = None) -> Any:
        if not BrickSidecar.enabled():
            return None

        url = '{base}{path}'.format(base=BrickSidecar.base_url(), path=path)

        try:
            response = requests.get(
                url,
                params=params,
                timeout=BrickSidecar.timeout(),
            )

            if not response.ok:
                logger.debug(
                    'sidecar GET %s -> HTTP %s', url, response.status_code,
                )
                return None

            return response.json()
        except (requests.RequestException, ValueError) as exception:
            # ValueError covers JSON decode errors. Never propagate.
            logger.debug('sidecar GET %s failed: %s', url, exception)
            return None

    # --- Health ---------------------------------------------------------

    # Cached short-TTL health probe. Safe to call on every render.
    @staticmethod
    def healthy() -> bool:
        if not BrickSidecar.enabled():
            return False

        now = time.monotonic()
        cache = BrickSidecar._health_cache
        if cache is not None and (now - cache[0]) < HEALTH_CACHE_TTL:
            return cache[1]

        payload = BrickSidecar._get_json('/health')
        healthy = bool(payload) and payload.get('status') == 'ok'

        BrickSidecar._health_cache = (now, healthy)
        return healthy

    # --- Sets -----------------------------------------------------------

    # GET /sets/{ref}. Returns the single set dict (the sidecar wraps it in a
    # {"sets": [...]} list) with the legoCom* JSON-string fields parsed into
    # dicts, or None if missing. When price=True, the BrickLink price block is
    # merged in under 'bricklink_price'.
    #
    # Metadata is read from the persistent cache first (effectively permanent);
    # pass refresh=True to force a network fetch and rewrite the cache.
    @staticmethod
    def get_set(
        ref: str,
        /,
        *,
        price: bool = False,
        refresh: bool = False,
        use_cache: bool = True,
    ) -> dict[str, Any] | None:
        # The sidecar (brickdata) is the single source of truth and cache: it
        # serves from its own DB and only hits Brickset on its own staleness
        # rules. We always read live from it — no second cache here. (use_cache
        # is kept for signature compatibility but no longer caches locally.)
        params: dict[str, Any] = {}
        if refresh:
            params['refresh'] = 'true'

        payload = BrickSidecar._get_json(
            '/sets/{ref}'.format(ref=ref),
            params=params or None,
        )

        if not payload:
            return None

        sets = payload.get('sets') or []
        if not sets:
            return None

        data = sets[0]

        # The sidecar serializes legoCom* as JSON strings; parse them so call
        # sites get a dict (or None) instead of a raw string.
        for region in RETAIL_REGIONS:
            key = 'legoCom{region}'.format(region=region)
            data[key] = BrickSidecar._parse_json_field(data.get(key))

        if price:
            data = dict(data)
            data['bricklink_price'] = BrickSidecar.get_price(ref, refresh=refresh)

        return data

    # BrickLink market value for a set, or None. The sidecar owns price caching
    # (and its own TTL): the normal path returns its cached price (fetching once
    # if its cache expired), while refresh=True forces a live re-fetch via the
    # dedicated /price endpoint. No local caching here.
    @staticmethod
    def get_price(
        ref: str,
        /,
        *,
        refresh: bool = False,
        use_cache: bool = True,
    ) -> dict[str, Any] | None:
        currency = str(current_app.config.get('SIDECAR_CURRENCY', '') or '').strip()

        # Forced refresh (explicit user action): the dedicated endpoint
        # re-fetches from BrickLink and rewrites the sidecar's price cache.
        if refresh:
            params: dict[str, Any] = {'refresh': 'true'}
            if currency:
                params['currency'] = currency
            return BrickSidecar._get_json(
                '/sets/{ref}/price'.format(ref=ref),
                params=params,
            )

        # Normal path: the sidecar returns its cached price, or fetches once if
        # its own TTL expired. The price rides along on the set payload under
        # bricklink_price. No local caching — the sidecar is the cache.
        params = {'price': 'true'}
        if currency:
            params['currency'] = currency

        payload = BrickSidecar._get_json(
            '/sets/{ref}'.format(ref=ref),
            params=params,
        )

        if payload:
            sets = payload.get('sets') or []
            if sets:
                return sets[0].get('bricklink_price') or None

        return None

    # GET /sets/bulk -> cached metadata (+ cached price) for many sets at once,
    # keyed by ref. The sidecar serves this from its own DB with no live
    # Brickset/BrickLink calls, so it is cheap enough for collection-wide
    # aggregation (stats) without a local cache. Requests are chunked to keep
    # the query string within sane limits.
    @staticmethod
    def get_sets_bulk(
        refs: list[str],
        /,
        *,
        price: bool = True,
        chunk_size: int = 200,
    ) -> dict[str, dict[str, Any]]:
        wanted = [r for r in refs if r]
        if not wanted:
            return {}

        currency = str(current_app.config.get('SIDECAR_CURRENCY', '') or '').strip()
        out: dict[str, dict[str, Any]] = {}

        for start in range(0, len(wanted), chunk_size):
            chunk = wanted[start:start + chunk_size]
            params: dict[str, Any] = {'refs': ','.join(chunk)}
            if price:
                params['price'] = 'true'
            if currency:
                params['currency'] = currency

            payload = BrickSidecar._get_json('/sets/bulk', params=params)
            if not payload:
                continue

            for s in payload.get('sets') or []:
                ref = '{n}-{v}'.format(
                    n=s.get('number'), v=s.get('numberVariant'),
                )
                for region in RETAIL_REGIONS:
                    key = 'legoCom{region}'.format(region=region)
                    s[key] = BrickSidecar._parse_json_field(s.get(key))
                out[ref] = s

        return out

    # Convenience: MSRP for the configured retail region (SIDECAR_RETAIL_REGION),
    # read from an already-fetched get_set() payload. None when unavailable.
    @staticmethod
    def retail_price(set_data: dict[str, Any], /) -> float | None:
        region = BrickSidecar.retail_region()
        block = set_data.get('legoCom{region}'.format(region=region))

        if not isinstance(block, dict):
            return None

        value = block.get('retailPrice')
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    # Configured retail region (US/UK/CA/DE), defaulting to US.
    @staticmethod
    def retail_region() -> str:
        region = str(current_app.config.get('SIDECAR_RETAIL_REGION', 'US')).upper()
        return region if region in REGION_CURRENCY else 'US'

    # Currency code for the configured retail region.
    @staticmethod
    def retail_currency() -> str:
        return REGION_CURRENCY[BrickSidecar.retail_region()]

    # The ISO code(s) a currency value can represent. An ISO code maps to itself;
    # a known symbol maps to its candidate set (see CURRENCY_SYMBOLS); anything
    # else falls back to its own uppercased form.
    @staticmethod
    def currency_codes(value: Any, /) -> set[str]:
        text = str(value or '').strip()
        if not text:
            return set()

        key = text.rstrip('.').lower()
        if key in CURRENCY_SYMBOLS:
            return set(CURRENCY_SYMBOLS[key])

        return {text.upper()}

    # Whether two currency values (symbol or ISO code) denote the same currency.
    # Empty values are treated as "unknown" -> compatible, so we never warn just
    # because one side is unset.
    @staticmethod
    def same_currency(a: Any, b: Any, /) -> bool:
        codes_a = BrickSidecar.currency_codes(a)
        codes_b = BrickSidecar.currency_codes(b)

        if not codes_a or not codes_b:
            return True

        return bool(codes_a & codes_b)

    # Read a price WITHOUT triggering a live BrickLink fetch: ask the sidecar
    # for a cache-only price (cached_only=true), so a render never blocks.
    # Returns (price_dict, fetched_at) or (None, None).
    @staticmethod
    def cached_price(ref: str, /) -> tuple[dict[str, Any] | None, Any]:
        params: dict[str, Any] = {'price': 'true', 'cached_only': 'true'}
        currency = str(current_app.config.get('SIDECAR_CURRENCY', '') or '').strip()
        if currency:
            params['currency'] = currency

        payload = BrickSidecar._get_json(
            '/sets/{ref}'.format(ref=ref),
            params=params,
        )

        price: dict[str, Any] | None = None
        if payload:
            sets = payload.get('sets') or []
            if sets:
                price = sets[0].get('bricklink_price') or None

        if price is None:
            return None, None

        return price, price.get('fetched_at')

    # --- Images ---------------------------------------------------------

    # GET /sets/{ref}/images -> {'brickset': {...}, 'bricklink': {...}}, or None.
    @staticmethod
    def get_images(ref: str, /) -> dict[str, Any] | None:
        return BrickSidecar._get_json('/sets/{ref}/images'.format(ref=ref))

    # Build the image-proxy URL for direct use in an <img src> (no server
    # round-trip needed to preview). Does not hit the network.
    @staticmethod
    def image_proxy_url(image_type: str, ref: str, /) -> str | None:
        if image_type not in IMAGE_TYPES or not BrickSidecar.enabled():
            return None

        return '{base}/images/bricklink/{type}/{ref}.png'.format(
            base=BrickSidecar.base_url(),
            type=image_type,
            ref=ref,
        )

    # Build the URL of one Brickset additional image (0-indexed) for direct use
    # in an <img src>. Unlike box/instruction art these come from Brickset, not
    # the BrickLink image proxy. Pass thumbnail=True for the smaller variant.
    # Does not hit the network. Returns None when the sidecar is disabled.
    @staticmethod
    def additional_image_url(
        ref: str,
        index: int,
        /,
        *,
        thumbnail: bool = False,
    ) -> str | None:
        if not BrickSidecar.enabled():
            return None

        url = '{base}/sets/{ref}/additional-images/{index}'.format(
            base=BrickSidecar.base_url(),
            ref=ref,
            index=index,
        )

        if thumbnail:
            url = '{url}?size=thumbnail'.format(url=url)

        return url

    # Fetch the raw bytes of one Brickset additional image (used when saving it
    # as the cover). Returns None on any failure or a 404.
    @staticmethod
    def fetch_additional_image_bytes(ref: str, index: int, /) -> bytes | None:
        url = BrickSidecar.additional_image_url(ref, index)
        if url is None:
            return None

        return BrickSidecar._fetch_bytes(url)

    # Fetch the raw bytes of a proxied image (used when saving box art locally).
    # Returns None on any failure or a 404 (BrickLink has no such image).
    @staticmethod
    def fetch_image_bytes(image_type: str, ref: str, /) -> bytes | None:
        url = BrickSidecar.image_proxy_url(image_type, ref)
        if url is None:
            return None

        return BrickSidecar._fetch_bytes(url)

    # Download the raw bytes at a sidecar image URL, returning None on any
    # failure or a non-OK status (e.g. a 404 when the image does not exist).
    @staticmethod
    def _fetch_bytes(url: str, /) -> bytes | None:
        try:
            response = requests.get(url, timeout=BrickSidecar.timeout())

            if not response.ok:
                logger.debug(
                    'sidecar image %s -> HTTP %s', url, response.status_code,
                )
                return None

            return response.content
        except requests.RequestException as exception:
            logger.debug('sidecar image %s failed: %s', url, exception)
            return None

    # --- Cover override -------------------------------------------------

    # Absolute path of the locally stored cover for a set ref, mirroring the
    # logic in RebrickableImage.path() (everything is stored as .jpg).
    @staticmethod
    def cover_path(set_ref: str, /) -> str:
        folder: str = current_app.config['SETS_FOLDER']

        if folder.startswith('/'):
            base_path = folder
        else:
            base_path = os.path.join(current_app.root_path, folder)

        return os.path.join(base_path, '{ref}.jpg'.format(ref=set_ref))

    # Backup path used so a box-art override is reversible.
    @staticmethod
    def cover_backup_path(set_ref: str, /) -> str:
        return BrickSidecar.cover_path(set_ref).replace('.jpg', '.bak.jpg')

    # Override the local cover image with a sidecar image (box / set). Backs up
    # the existing cover the first time so it can be restored. Returns True on
    # success, False if the sidecar has no such image or anything fails.
    @staticmethod
    def save_cover_override(set_ref: str, image_type: str, /) -> bool:
        data = BrickSidecar.fetch_image_bytes(image_type, set_ref)
        return BrickSidecar._write_cover(set_ref, data)

    # Override the local cover with one Brickset additional image (0-indexed).
    # Same backup/restore semantics as save_cover_override.
    @staticmethod
    def save_cover_override_from_additional(set_ref: str, index: int, /) -> bool:
        data = BrickSidecar.fetch_additional_image_bytes(set_ref, index)
        return BrickSidecar._write_cover(set_ref, data)

    # Write image bytes as the local cover, backing up the original Rebrickable
    # cover once so it stays restorable. Returns False when data is None (the
    # sidecar had no such image) or on any filesystem error.
    @staticmethod
    def _write_cover(set_ref: str, data: bytes | None, /) -> bool:
        if data is None:
            return False

        path = BrickSidecar.cover_path(set_ref)
        backup = BrickSidecar.cover_backup_path(set_ref)

        try:
            # Preserve the original Rebrickable cover once.
            if os.path.exists(path) and not os.path.exists(backup):
                os.replace(path, backup)
                # os.replace moved the file; re-create it below from bytes.

            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as handle:
                handle.write(data)

            return True
        except OSError as exception:
            logger.debug('cover override for %s failed: %s', set_ref, exception)
            return False

    # Restore a previously backed-up Rebrickable cover. Returns True if a backup
    # existed and was restored, False otherwise (caller may re-download instead).
    @staticmethod
    def restore_cover(set_ref: str, /) -> bool:
        path = BrickSidecar.cover_path(set_ref)
        backup = BrickSidecar.cover_backup_path(set_ref)

        if not os.path.exists(backup):
            return False

        try:
            os.replace(backup, path)
            return True
        except OSError as exception:
            logger.debug('cover restore for %s failed: %s', set_ref, exception)
            return False

    # --- Internal -------------------------------------------------------

    # Parse a field the sidecar returns as a JSON string into a dict, tolerating
    # None / empty / malformed values.
    @staticmethod
    def _parse_json_field(value: Any) -> dict[str, Any] | None:
        if not value:
            return None

        if isinstance(value, dict):
            return value

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, dict) else None
            except ValueError:
                return None

        return None
