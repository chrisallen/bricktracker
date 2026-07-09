import logging
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any

from flask import current_app, url_for
from markupsafe import Markup, escape

from .bag_part import list_state as list_bag_part_state
from .sidecar import BrickSidecar

logger = logging.getLogger(__name__)

# Brickset descriptions ship as HTML (<p>, <ul>, <li>, <i>, ...). Keep only a
# small allowlist of formatting tags and drop every attribute so the markup can
# be rendered as-is without opening an XSS hole.
_ALLOWED_TAGS = frozenset({
    'p', 'br', 'ul', 'ol', 'li', 'b', 'strong', 'i', 'em', 'u',
    'h3', 'h4', 'h5', 'h6', 'small', 'sub', 'sup',
})
_VOID_TAGS = frozenset({'br'})


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
        'description': _description(data.get('description')),
        'pieces': data.get('pieces'),
        'minifigs': data.get('minifigs'),
        'year': data.get('year'),
        'theme': _clean_str(data.get('theme')),
        'subtheme': _clean_str(data.get('subtheme')),
        # Set designer(s); web-scraped, the API does not expose it.
        'designer': _clean_str(data.get('designer')),
        'dimensions': _dimensions(data),
        'weight': _weight(data),
        'instructions_count': data.get('instructionsCount'),
        'additional_image_count': _to_int(data.get('additionalImageCount')),
        # Carousel + extra cover sources are opt-in; off keeps the plain cover.
        'additional_images_enabled': bool(
            current_app.config['SIDECAR_ADDITIONAL_IMAGES']
        ),
        'tags': _tags(data.get('tags')),
        # Brickset "Notes" blurb (web-scraped; contains light HTML). Sanitised
        # like the description so it renders safely.
        'notes': _description(data.get('notes')),
        # Whether the sidecar holds a per-bag part inventory for this set.
        'has_bags': bool(data.get('has_bags')),
    }

    # Retired status from the exit date. exit_date is the full formatted date
    # (BrickData/Brickset has it even for sets retired long ago, which the
    # upcoming-retirements CSV does not cover, see #37).
    retired, exit_year = _retired(data.get('exitDate'))
    summary['retired'] = retired
    summary['exit_year'] = exit_year
    summary['exit_date'] = _format_date(data.get('exitDate'))
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
        # Inflation-adjusted RRP, web-scraped by the sidecar (single value in
        # its own currency, independent of the configured retail region).
        'msrp_inflated': _to_float(data.get('rrpInflated')),
        'msrp_inflated_currency': _clean_str(data.get('rrpInflatedCurrency')),
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

    # Value movement vs what was paid. SIDECAR_PRICE_BASIS picks which market
    # average to compare against ('used' or 'new'); fall back to the other when
    # the preferred one is missing.
    basis = str(current_app.config.get('SIDECAR_PRICE_BASIS', 'used')).lower()
    if basis == 'new':
        market_ref = market_new if market_new is not None else market_used
    else:
        market_ref = market_used if market_used is not None else market_new
    prices['market_basis'] = basis
    if market_ref is not None and paid is not None:
        prices['gain_vs_paid'] = round(market_ref - paid, 2)

    summary['prices'] = prices

    return summary


# Join the sidecar's per-bag inventory onto the set's part rows. Returns
# (bags, breakdown):
# - bags: template-ready [{'number', 'is_extra', 'parts': [...]}] in sidecar
#   order, each part carrying its per-bag quantity, display data, the stored
#   per-bag checked/missing state with its changer prefixes/urls, and the DOM
#   id of the main row's missing input (the sum-group key for the client-side
#   missing sync).
# - breakdown: part row html_id() -> [[bag number, quantity], ...] pairs, for
#   the bag column in the normal audit modal.
# Degrades to (None, {}) whenever the sidecar is off or has no bag data; the
# bag composition is joined at render time and never persisted (only the
# per-bag progress lives in bricktracker_bag_parts).
def bag_inventory(
    brickset: Any,
    parts: Any,
    /,
) -> tuple[list[dict[str, Any]] | None, dict[str, list[list[Any]]]]:
    if not BrickSidecar.enabled():
        return None, {}

    payload = BrickSidecar.get_bags(brickset.fields.set)
    if not payload or not payload.get('bags'):
        return None, {}

    # One BrickTracker row per (part, color, spare) for the whole set; bag
    # entries reference it many-to-one via (part_ex_id, color_id).
    index: dict[tuple[str, int, int], Any] = {
        (str(row.fields.part), int(row.fields.color), int(row.fields.spare)): row  # noqa: E501
        for row in parts
    }

    # Stored per-bag progress, keyed (bag, part, color, spare)
    state = list_bag_part_state(brickset.fields.id)

    # The changer prefixes keep the "-missing-"/"-checked-" fragments so the
    # bulk operations and audit selectors match, and a per-bag "bag{i}"
    # namespace so ids stay unique across bags.
    def changer(index: int, kind: str, part: str, color: int, spare: int, bag: str) -> dict[str, Any]:  # noqa: E501
        return {
            'prefix_{kind}'.format(kind=kind): 'bag{index}-part-{kind}-{part}-{color}-{spare}'.format(  # noqa: E501
                index=index, kind=kind, part=part, color=color, spare=spare,
            ),
            'url_{kind}'.format(kind=kind): url_for(
                'set.bag_part_state',
                id=brickset.fields.id,
                bag=bag,
                part=part,
                color=color,
                spare=spare,
                state=kind,
            ),
        }

    bags: list[dict[str, Any]] = []
    breakdown: dict[str, list[list[Any]]] = {}

    for i, bag in enumerate(payload['bags'], start=1):
        number = str(bag.get('displayNumbers') or bag.get('bagNumber') or '?')
        # "Extra" bags sometimes hold the spares, so try spare rows first
        # there (with a fallback either way, see spare_order below)
        is_extra = number.lower() == 'extra'
        spare_order = (1, 0) if is_extra else (0, 1)

        bag_parts: list[dict[str, Any]] = []
        for part in bag.get('parts') or []:
            part_ref = str(part.get('part_ex_id') or part.get('bl_part_id') or '')  # noqa: E501
            try:
                color = int(part.get('color_id'))
            except (TypeError, ValueError):
                color = -1
            quantity = part.get('quantity') or 0

            row = None
            for spare in spare_order:
                row = index.get((part_ref, color, spare))
                if row is not None:
                    break

            if row is not None:
                part_state = state.get(
                    (number, row.fields.part, row.fields.color, row.fields.spare),  # noqa: E501
                    {},
                )
                entry: dict[str, Any] = {
                    'quantity': quantity,
                    'name': row.fields.name,
                    'color': row.fields.color,
                    'color_name': row.fields.color_name,
                    'color_rgb': row.fields.color_rgb,
                    'spare': bool(row.fields.spare),
                    'image_url': row.url_for_image(),
                    'url': row.url(),
                    # Final DOM id of the main row's missing input
                    # (macro/form.html renders "{prefix}-{id}").
                    'missing_input_id': '{prefix}-{id}'.format(
                        prefix=row.html_id('missing'),
                        id=row.fields.id,
                    ),
                    'checked': part_state.get('checked', False),
                    # None renders an empty input, like the main table
                    'missing': part_state.get('missing') or None,
                }
                entry.update(changer(i, 'missing', row.fields.part, row.fields.color, row.fields.spare, number))  # noqa: E501
                entry.update(changer(i, 'checked', row.fields.part, row.fields.color, row.fields.spare, number))  # noqa: E501
                bag_parts.append(entry)
                breakdown.setdefault(row.html_id(), []).append(
                    [number, quantity],
                )
            else:
                # No matching row (e.g. a part the import assigned to a
                # minifigure): display-only data from the sidecar, but the
                # per-bag progress is still stored (keyed by the sidecar
                # part ref, spare=0). A negative color means the sidecar
                # gave no usable identity, so the row gets no inputs.
                part_state = state.get((number, part_ref, color, 0), {})
                entry = {
                    'quantity': quantity,
                    'name': part_ref or str(part.get('partId') or '?'),
                    'color': None,
                    'color_name': part.get('colorName'),
                    'color_rgb': str(part.get('colorHex') or '').lstrip('#') or None,  # noqa: E501
                    'spare': False,
                    'image_url': None,
                    'url': None,
                    'missing_input_id': None,
                    'checked': part_state.get('checked', False),
                    'missing': part_state.get('missing') or None,
                }
                if part_ref and color >= 0:
                    entry.update(changer(i, 'missing', part_ref, color, 0, number))  # noqa: E501
                    entry.update(changer(i, 'checked', part_ref, color, 0, number))  # noqa: E501
                bag_parts.append(entry)

        bags.append({
            'number': number,
            'is_extra': is_extra,
            'parts': bag_parts,
        })

    return bags, breakdown


# --- Helpers ------------------------------------------------------------

def _clean_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


# Rebuild an HTML fragment keeping only the allowlisted formatting tags, with
# all attributes stripped and all text escaped. convert_charrefs=True turns
# entities (&reg;, &#39;, ...) into real characters before they reach the data
# handler, so they render correctly.
class _DescriptionSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag in _ALLOWED_TAGS:
            self.parts.append(f'<{tag}>')

    def handle_startendtag(self, tag: str, attrs: Any) -> None:
        if tag in _ALLOWED_TAGS:
            self.parts.append(f'<{tag}>')

    def handle_endtag(self, tag: str) -> None:
        if tag in _ALLOWED_TAGS and tag not in _VOID_TAGS:
            self.parts.append(f'</{tag}>')

    def handle_data(self, data: str) -> None:
        self.parts.append(str(escape(data)))


def _description(value: Any) -> Markup | None:
    text = _clean_str(value)
    if text is None:
        return None
    parser = _DescriptionSanitizer()
    parser.feed(text)
    parser.close()
    cleaned = ''.join(parser.parts)
    # Brickset pads descriptions with empty spacer paragraphs (<p>&nbsp;</p>);
    # drop those so the blocks sit flush instead of leaving big gaps. \s also
    # matches the &nbsp; (\xa0) the parser leaves behind.
    cleaned = re.sub(r'<p>\s*</p>', '', cleaned).strip()
    return Markup(cleaned) if cleaned else None


def _to_float(value: Any) -> float | None:
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    if value is None or value == '':
        return None
    try:
        return int(value)
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


def _format_date(value: Any) -> str | None:
    parsed = _parse_date(value)
    if parsed is None:
        return None
    return parsed.strftime(current_app.config['PURCHASE_DATE_FORMAT'])


def _retired(exit_date: Any) -> tuple[bool, int | None]:
    parsed = _parse_date(exit_date)
    if parsed is None:
        return False, None
    return parsed < datetime.now(timezone.utc), parsed.year


# Bulk retirement lookup for a list of set refs (e.g. the whole wishlist) in a
# single cached BrickData call. Returns {ref: {'date': str|None,
# 'retired': bool}} keyed by both "number-variant" and the bare number so the
# caller can match whichever form it stores. Empty dict when the sidecar is
# disabled or unreachable, so callers degrade to the CSV (see #37).
def retirement_dates(
    set_refs: Any,
    /,
) -> dict[str, dict[str, Any]]:
    if not BrickSidecar.enabled():
        return {}

    refs = list({str(ref) for ref in set_refs if ref})
    if not refs:
        return {}

    try:
        bulk = BrickSidecar.get_sets_bulk(refs, price=False)
    except Exception as exception:
        logger.debug('sidecar retirement bulk fetch failed: %s', exception)
        return {}

    out: dict[str, dict[str, Any]] = {}
    for ref, data in bulk.items():
        retired, _ = _retired(data.get('exitDate'))
        info = {
            'date': _format_date(data.get('exitDate')),
            'retired': retired,
        }
        out[ref] = info
        number, _, _ = ref.partition('-')
        out.setdefault(number, info)

    return out
