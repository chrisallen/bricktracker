from typing import Any, Final

# Configuration map:
# - n: internal name (str)
# - e: extra environment name (str, optional=None)
# - d: default value (Any, optional=None)
# - c: cast to type (Type, optional=None)
# - s: interpret as a path within static (bool, optional=False)
# Easy to change an environment variable name without changing all the code
CONFIG: Final[list[dict[str, Any]]] = [
    {'n': 'AUTHENTICATION_PASSWORD', 'd': ''},
    {'n': 'AUTHENTICATION_KEY', 'd': ''},
    # BrickLink minifigure links disabled - Rebrickable doesn't provide BrickLink minifigure IDs
    # {'n': 'BRICKLINK_LINK_MINIFIGURE_PATTERN', 'd': 'https://www.bricklink.com/v2/catalog/catalogitem.page?M={figure}'},  # noqa: E501
    {'n': 'BRICKLINK_LINK_PART_PATTERN', 'd': 'https://www.bricklink.com/v2/catalog/catalogitem.page?P={part}&C={color}'},  # noqa: E501
    {'n': 'BRICKLINK_LINK_SET_PATTERN', 'd': 'https://www.bricklink.com/v2/catalog/catalogitem.page?S={set_num}'},  # noqa: E501
    {'n': 'BRICKLINK_LINKS', 'c': bool},
    {'n': 'DATABASE_PATH', 'd': 'data/app.db'},
    {'n': 'DATABASE_TIMESTAMP_FORMAT', 'd': '%Y-%m-%d-%H-%M-%S'},
    {'n': 'DEBUG', 'c': bool},
    {'n': 'DEFAULT_TABLE_PER_PAGE', 'd': 25, 'c': int},
    {'n': 'DISABLE_INDIVIDUAL_MINIFIGURES', 'c': bool},
    {'n': 'DISABLE_INDIVIDUAL_PARTS', 'c': bool},
    {'n': 'DISABLE_QUICK_ADD_INDIVIDUAL_PARTS', 'c': bool},
    {'n': 'HIDE_QUICK_ADD_INDIVIDUAL_PARTS', 'c': bool},
    {'n': 'DOMAIN_NAME', 'e': 'DOMAIN_NAME', 'd': ''},
    {'n': 'FILE_DATETIME_FORMAT', 'd': '%d/%m/%Y, %H:%M:%S'},
    {'n': 'HOST', 'd': '0.0.0.0'},
    {'n': 'INDEPENDENT_ACCORDIONS', 'c': bool},
    {'n': 'INSTRUCTIONS_ALLOWED_EXTENSIONS', 'd': ['.pdf'], 'c': list},  # noqa: E501
    {'n': 'INSTRUCTIONS_FOLDER', 'd': 'data/instructions'},
    {'n': 'HIDE_ADD_SET', 'c': bool},
    {'n': 'HIDE_ADD_BULK_SET', 'c': bool},
    {'n': 'HIDE_ADMIN', 'c': bool},
    {'n': 'ADMIN_DEFAULT_EXPANDED_SECTIONS', 'd': ['database'], 'c': list},
    {'n': 'HIDE_ALL_INSTRUCTIONS', 'c': bool},
    {'n': 'HIDE_ALL_MINIFIGURES', 'c': bool},
    {'n': 'HIDE_INDIVIDUAL_MINIFIGURES', 'c': bool},
    {'n': 'HIDE_ALL_PARTS', 'c': bool},
    {'n': 'HIDE_INDIVIDUAL_PARTS', 'c': bool},
    {'n': 'HIDE_ALL_PROBLEMS_PARTS', 'e': 'BK_HIDE_MISSING_PARTS', 'c': bool},
    {'n': 'HIDE_ALL_SETS', 'c': bool},
    {'n': 'HIDE_ALL_STORAGES', 'c': bool},
    {'n': 'HIDE_STATISTICS', 'c': bool},
    {'n': 'HIDE_SET_INSTRUCTIONS', 'c': bool},
    {'n': 'HIDE_TABLE_DAMAGED_PARTS', 'c': bool},
    {'n': 'HIDE_TABLE_MISSING_PARTS', 'c': bool},
    {'n': 'HIDE_TABLE_CHECKED_PARTS', 'c': bool},
    {'n': 'HIDE_WISHES', 'c': bool},
    {'n': 'MINIFIGURES_DEFAULT_ORDER', 'd': '"rebrickable_minifigures"."name" ASC'},  # noqa: E501
    {'n': 'MINIFIGURES_FOLDER', 'd': 'data/minifigures'},
    {'n': 'MINIFIGURES_PAGINATION_SIZE_DESKTOP', 'd': 10, 'c': int},
    {'n': 'MINIFIGURES_PAGINATION_SIZE_MOBILE', 'd': 5, 'c': int},
    {'n': 'MINIFIGURES_SERVER_SIDE_PAGINATION', 'c': bool},
    {'n': 'NO_THREADED_SOCKET', 'c': bool},
    {'n': 'PARTS_SERVER_SIDE_PAGINATION', 'c': bool},
    {'n': 'SETS_SERVER_SIDE_PAGINATION', 'c': bool},
    {'n': 'PARTS_DEFAULT_ORDER', 'd': '"rebrickable_parts"."name" ASC, "rebrickable_parts"."color_name" ASC, "combined"."spare" ASC'},  # noqa: E501
    {'n': 'PARTS_FOLDER', 'd': 'data/parts'},
    {'n': 'PARTS_PAGINATION_SIZE_DESKTOP', 'd': 10, 'c': int},
    {'n': 'PARTS_PAGINATION_SIZE_MOBILE', 'd': 5, 'c': int},
    {'n': 'PROBLEMS_PAGINATION_SIZE_DESKTOP', 'd': 10, 'c': int},
    {'n': 'PROBLEMS_PAGINATION_SIZE_MOBILE', 'd': 10, 'c': int},
    {'n': 'PROBLEMS_SERVER_SIDE_PAGINATION', 'c': bool},
    {'n': 'SETS_PAGINATION_SIZE_DESKTOP', 'd': 12, 'c': int},
    {'n': 'SETS_PAGINATION_SIZE_MOBILE', 'd': 4, 'c': int},
    {'n': 'PORT', 'd': 3333, 'c': int},
    {'n': 'PURCHASE_DATE_FORMAT', 'd': '%d/%m/%Y'},
    {'n': 'PURCHASE_CURRENCY', 'd': '€'},
    {'n': 'PURCHASE_LOCATION_DEFAULT_ORDER', 'd': '"bricktracker_metadata_purchase_locations"."name" ASC'},  # noqa: E501
    {'n': 'RANDOM', 'e': 'RANDOM', 'c': bool},
    {'n': 'REBRICKABLE_API_KEY', 'e': 'REBRICKABLE_API_KEY', 'd': ''},
    {'n': 'REBRICKABLE_IMAGE_NIL', 'd': 'https://rebrickable.com/static/img/nil.png'},  # noqa: E501
    {'n': 'REBRICKABLE_IMAGE_NIL_MINIFIGURE', 'd': 'https://rebrickable.com/static/img/nil_mf.jpg'},  # noqa: E501
    {'n': 'REBRICKABLE_LINK_MINIFIGURE_PATTERN', 'd': 'https://rebrickable.com/minifigs/{figure}'},  # noqa: E501
    {'n': 'REBRICKABLE_LINK_PART_PATTERN', 'd': 'https://rebrickable.com/parts/{part}/_/{color}'},  # noqa: E501
    {'n': 'REBRICKABLE_LINK_INSTRUCTIONS_PATTERN', 'd': 'https://rebrickable.com/instructions/{path}'},  # noqa: E501
    {'n': 'REBRICKABLE_USER_AGENT', 'd': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},  # noqa: E501
    {'n': 'USER_AGENT', 'd': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},  # noqa: E501
    {'n': 'PEERON_DOWNLOAD_DELAY', 'd': 1000, 'c': int},
    {'n': 'PEERON_INSTRUCTION_PATTERN', 'd': 'http://peeron.com/scans/{set_number}-{version_number}'},
    {'n': 'PEERON_MIN_IMAGE_SIZE', 'd': 100, 'c': int},
    {'n': 'PEERON_SCAN_PATTERN', 'd': 'http://belay.peeron.com/scans/{set_number}-{version_number}/'},
    {'n': 'PEERON_THUMBNAIL_PATTERN', 'd': 'http://belay.peeron.com/thumbs/{set_number}-{version_number}/'},
    {'n': 'REBRICKABLE_LINKS', 'e': 'LINKS', 'c': bool},
    {'n': 'REBRICKABLE_PAGE_SIZE', 'd': 100, 'c': int},
    {'n': 'RETIRED_SETS_FILE_URL', 'd': 'https://docs.google.com/spreadsheets/d/1rlYfEXtNKxUOZt2Mfv0H17DvK7bj6Pe0CuYwq6ay8WA/gviz/tq?tqx=out:csv&sheet=Sorted%20by%20Retirement%20Date'},  # noqa: E501
    {'n': 'RETIRED_SETS_PATH', 'd': 'data/retired_sets.csv'},
    {'n': 'SETS_DEFAULT_ORDER', 'd': '"rebrickable_sets"."number" DESC, "rebrickable_sets"."version" ASC'},  # noqa: E501
    {'n': 'SETS_FOLDER', 'd': 'data/sets'},
    {'n': 'SETS_CONSOLIDATION', 'd': False, 'c': bool},
    {'n': 'SHOW_GRID_FILTERS', 'c': bool},
    {'n': 'SHOW_GRID_SORT', 'c': bool},
    {'n': 'SHOW_SETS_DUPLICATE_FILTER', 'd': True, 'c': bool},
    {'n': 'SKIP_SPARE_PARTS', 'c': bool},
    {'n': 'HIDE_SPARE_PARTS', 'c': bool},
    {'n': 'SOCKET_NAMESPACE', 'd': 'bricksocket'},
    {'n': 'SOCKET_PATH', 'd': '/bricksocket/'},
    {'n': 'STORAGE_DEFAULT_ORDER', 'd': '"bricktracker_metadata_storages"."name" ASC'},  # noqa: E501
    {'n': 'THEMES_FILE_URL', 'd': 'https://cdn.rebrickable.com/media/downloads/themes.csv.gz'},  # noqa: E501
    {'n': 'THEMES_PATH', 'd': 'data/themes.csv'},
    {'n': 'TIMEZONE', 'd': 'Etc/UTC'},
    {'n': 'USE_REMOTE_IMAGES', 'c': bool},
    {'n': 'WISHES_DEFAULT_ORDER', 'd': '"bricktracker_wishes"."rowid" DESC'},
    {'n': 'STATISTICS_SHOW_CHARTS', 'd': True, 'c': bool},
    {'n': 'STATISTICS_DEFAULT_EXPANDED', 'd': True, 'c': bool},
    {'n': 'DARK_MODE', 'c': bool},
    {'n': 'BADGE_ORDER_GRID', 'd': ['theme', 'year', 'parts', 'total_minifigures', 'instructions', 'owner'], 'c': list},
    {'n': 'BADGE_ORDER_DETAIL', 'd': ['theme', 'tag', 'year', 'retired', 'parts', 'instance_count', 'total_minifigures', 'total_missing', 'total_damaged', 'owner', 'storage', 'purchase_date', 'purchase_location', 'purchase_price', 'msrp', 'value', 'dimensions', 'weight', 'instructions', 'rebrickable', 'bricklink'], 'c': list},
    {'n': 'SHOW_NOTES_GRID', 'd': False, 'c': bool},
    {'n': 'SHOW_NOTES_DETAIL', 'd': True, 'c': bool},
    # Sidecar (brickset-sidecar / BrickData) integration. Opt-in: an empty
    # SIDECAR_URL means the whole feature is off and everything degrades.
    {'n': 'SIDECAR_URL', 'd': ''},
    {'n': 'SIDECAR_TIMEOUT', 'd': 5, 'c': int},
    {'n': 'SIDECAR_DEFAULT_COVER', 'd': 'rebrickable'},
    # Opt-in browsing of every BrickLink image the sidecar exposes for a set
    # (a carousel on the detail page + extra cover sources). Off keeps the
    # plain single cover behaviour.
    {'n': 'SIDECAR_ADDITIONAL_IMAGES', 'd': False, 'c': bool},
    {'n': 'SIDECAR_RETAIL_REGION', 'd': 'US'},
    {'n': 'SIDECAR_AUTO_FETCH_PRICE', 'c': bool},
    # Currency to request BrickLink market values in (e.g. EUR). Empty lets the
    # sidecar use its default. Sent as a query parameter only when set; sidecars
    # that do not support it simply ignore it.
    {'n': 'SIDECAR_CURRENCY', 'd': ''},
    # Manual exchange rate used to convert MSRP into PURCHASE_CURRENCY, since
    # Brickset only publishes retail prices in the region's own currency (USD
    # for US, GBP for UK, ...). Value is "how many PURCHASE_CURRENCY units one
    # unit of the region currency is worth", e.g. 6.47 for USD -> DKK. Empty or
    # 0 leaves MSRP untouched in its original currency. Kept as a string here
    # and parsed defensively, so a typo cannot break startup.
    {'n': 'SIDECAR_MSRP_RATE', 'd': ''},
    # Per-element show/hide toggles for the BrickData enrichment on the set
    # detail page. All default on so behaviour is unchanged; badges are handled
    # separately via BADGE_ORDER_DETAIL.
    {'n': 'SIDECAR_SHOW_DESIGNER', 'd': True, 'c': bool},
    {'n': 'SIDECAR_SHOW_DESCRIPTION', 'd': True, 'c': bool},
    {'n': 'SIDECAR_SHOW_NOTES', 'd': True, 'c': bool},
    {'n': 'SIDECAR_SHOW_PRICE_PAID', 'd': True, 'c': bool},
    {'n': 'SIDECAR_SHOW_PRICE_MSRP', 'd': True, 'c': bool},
    {'n': 'SIDECAR_SHOW_PRICE_MARKET', 'd': True, 'c': bool},
    # Which BrickLink market value the set-detail "Change vs paid" compares
    # against: 'used' or 'new'. Statistics shows both regardless.
    {'n': 'SIDECAR_PRICE_BASIS', 'd': 'used'},
    # Opt-in anonymous telemetry (see bricktracker/telemetry.py). Off by
    # default; only takes effect after a restart, by design, so "off" is
    # always certain. TELEMETRY_INSTALLATION_ID is intentionally absent from
    # the admin UI and from LIVE_CHANGEABLE_VARS/RESTART_REQUIRED_VARS in
    # config_manager.py. It is generated once by BrickTelemetry and never
    # user-editable.
    {'n': 'TELEMETRY_ENABLED', 'c': bool},
    {'n': 'TELEMETRY_PROMPTED', 'c': bool},
    {'n': 'TELEMETRY_CATEGORY_INSTALLATION', 'd': True, 'c': bool},
    {'n': 'TELEMETRY_CATEGORY_USAGE', 'd': True, 'c': bool},
    {'n': 'TELEMETRY_CATEGORY_COLLECTION', 'd': True, 'c': bool},
    {'n': 'TELEMETRY_INSTALLATION_ID', 'd': ''},
    # Where queued-but-not-yet-flushed telemetry events are persisted between
    # sends. Internal implementation detail, not user-editable. Absent from
    # LIVE_CHANGEABLE_VARS/RESTART_REQUIRED_VARS like TELEMETRY_INSTALLATION_ID.
    {'n': 'TELEMETRY_QUEUE_PATH', 'd': 'data/telemetry_queue.json'},
]
