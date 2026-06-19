import logging
from datetime import datetime, timezone
from typing import Any

from .sidecar import BrickSidecar

logger = logging.getLogger(__name__)


# Build a normalized, template-friendly summary of the sidecar data for a set:
# enrichment (description, dimensions, retired, ...) plus the three-way price
# comparison (paid / retail MSRP / BrickLink market value).
#
# Metadata comes from the persistent cache (a local read, effectively
# permanent). The BrickLink
# market value is read from cache only here (no network) so a page render never
# blocks; refreshing it is an explicit user action. Returns None when the
# sidecar is disabled or has no data for the set.
def summarize(
    set_ref: str,
    /,
    *,
    purchase_price: float | None = None,
    fetch_price: bool = False,
) -> dict[str, Any] | None:
    if not BrickSidecar.enabled():
        return None

    data = BrickSidecar.get_set(set_ref)
    if data is None:
        return None

    summary: dict[str, Any] = {
        'description': _clean_str(data.get('description')),
        'pieces': data.get('pieces'),
        'minifigs': data.get('minifigs'),
        'year': data.get('year'),
        'theme': _clean_str(data.get('theme')),
        'subtheme': _clean_str(data.get('subtheme')),
        'dimensions': _dimensions(data),
        'weight': _weight(data),
        'instructions_count': data.get('instructionsCount'),
        'additional_image_count': data.get('additionalImageCount'),
        'tags': _tags(data.get('tags')),
    }

    # Retired status from the exit date.
    retired, exit_year = _retired(data.get('exitDate'))
    summary['retired'] = retired
    summary['exit_year'] = exit_year
    summary['launch_year'] = _year(data.get('launchDate'))

    # --- Prices: paid / retail / market --------------------------------
    msrp = BrickSidecar.retail_price(data)

    # When auto-fetch is on, hit the TTL-aware path (network only on a cache
    # miss/expiry); otherwise stay cache-only so the render never blocks.
    if fetch_price:
        price_payload = BrickSidecar.get_price(set_ref)
        price_fetched_at = None
    else:
        price_payload, price_fetched_at = BrickSidecar.cached_price(set_ref)

    market_new = _to_float(price_payload.get('new_avg')) if price_payload else None
    market_used = _to_float(price_payload.get('used_avg')) if price_payload else None
    paid = _to_float(purchase_price)

    prices: dict[str, Any] = {
        'paid': paid,
        'msrp': msrp,
        'msrp_currency': BrickSidecar.retail_currency(),
        'market_new': market_new,
        'market_used': market_used,
        'market_min': _to_float(price_payload.get('new_min')) if price_payload else None,  # noqa: E501
        'market_max': _to_float(price_payload.get('new_max')) if price_payload else None,  # noqa: E501
        'market_used_min': _to_float(price_payload.get('used_min')) if price_payload else None,  # noqa: E501
        'market_used_max': _to_float(price_payload.get('used_max')) if price_payload else None,  # noqa: E501
        'market_currency': (price_payload or {}).get('currency_code'),
        'market_fetched_at': (price_payload or {}).get('fetched_at') or price_fetched_at,  # noqa: E501
        'has_market': price_payload is not None,
    }

    # Savings vs MSRP (positive = paid less than retail).
    if msrp is not None and paid is not None:
        prices['savings_vs_msrp'] = round(msrp - paid, 2)

    # Value movement vs what was paid (using the sealed/new market average,
    # falling back to used).
    market_ref = market_new if market_new is not None else market_used
    if market_ref is not None and paid is not None:
        prices['gain_vs_paid'] = round(market_ref - paid, 2)

    summary['prices'] = prices

    return summary


# --- Helpers ------------------------------------------------------------

def _clean_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_float(value: Any) -> float | None:
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _dimensions(data: dict[str, Any], /) -> str | None:
    height = _to_float(data.get('height'))
    width = _to_float(data.get('width'))
    depth = _to_float(data.get('depth'))

    if height is None and width is None and depth is None:
        return None

    parts = [
        '{0:g}'.format(round(value, 1)) if value is not None else '?'
        for value in (height, width, depth)
    ]
    return '{0} cm'.format(' × '.join(parts))


def _weight(data: dict[str, Any], /) -> str | None:
    weight = _to_float(data.get('weight'))
    if weight is None:
        return None
    return '{0:g} kg'.format(round(weight, 2))


def _tags(value: Any) -> list[str]:
    if not value:
        return []
    return [tag.strip() for tag in str(value).split(',') if tag.strip()]


def _parse_date(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).replace('Z', '+00:00')
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _year(value: Any) -> int | None:
    parsed = _parse_date(value)
    return parsed.year if parsed is not None else None


def _retired(exit_date: Any) -> tuple[bool, int | None]:
    parsed = _parse_date(exit_date)
    if parsed is None:
        return False, None
    return parsed < datetime.now(timezone.utc), parsed.year
