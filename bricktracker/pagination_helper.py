from flask import current_app, request
from typing import Any, Dict, Tuple


def get_pagination_config(entity_type: str) -> Tuple[int, bool]:
    """Get pagination configuration for an entity type (sets, parts, minifigures)"""
    # Check if pagination is enabled for this specific entity type
    pagination_key = f'{entity_type.upper()}_SERVER_SIDE_PAGINATION'
    use_pagination = current_app.config.get(pagination_key, False)

    if not use_pagination:
        return 0, False

    # Determine page size based on device type and entity
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad'])

    # Get appropriate config keys based on entity type
    entity_upper = entity_type.upper()
    desktop_key = f'{entity_upper}_PAGINATION_SIZE_DESKTOP'
    mobile_key = f'{entity_upper}_PAGINATION_SIZE_MOBILE'

    per_page = current_app.config[mobile_key] if is_mobile else current_app.config[desktop_key]

    return per_page, is_mobile


def build_pagination_context(page: int, per_page: int, total_count: int, is_mobile: bool) -> Dict[str, Any]:
    """Build pagination context for templates"""
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    has_prev = page > 1
    has_next = page < total_pages

    return {
        'page': page,
        'per_page': per_page,
        'total_count': total_count,
        'total_pages': total_pages,
        'has_prev': has_prev,
        'has_next': has_next,
        'is_mobile': is_mobile
    }


def get_request_params() -> Tuple[str, str, str, int]:
    """Extract common request parameters for pagination"""
    search_query = request.args.get('search', '').strip()
    sort_field = request.args.get('sort', '')
    sort_order = request.args.get('order', 'asc')
    page = int(request.args.get('page', 1))

    return search_query, sort_field, sort_order, page