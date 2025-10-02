"""
Statistics views for BrickTracker
Provides statistics and analytics pages
"""

import logging

from flask import Blueprint, render_template, request, url_for, redirect, current_app
from werkzeug.wrappers.response import Response

from .exceptions import exception_handler
from ..statistics import BrickStatistics

logger = logging.getLogger(__name__)

statistics_page = Blueprint('statistics', __name__, url_prefix='/statistics')


@statistics_page.route('/', methods=['GET'])
@exception_handler(__file__)
def overview() -> str:
    """Statistics overview page with metrics"""

    stats = BrickStatistics()

    # Get all statistics data
    overview_stats = stats.get_overview()
    theme_stats = stats.get_theme_statistics()
    storage_stats = stats.get_storage_statistics()
    purchase_location_stats = stats.get_purchase_location_statistics()
    financial_summary = stats.get_financial_summary()
    collection_summary = stats.get_collection_summary()
    sets_by_year_stats = stats.get_sets_by_year_statistics()
    purchases_by_year_stats = stats.get_purchases_by_year_statistics()
    year_summary = stats.get_year_summary()

    # Prepare chart data for visualization (only if charts are enabled)
    chart_data = {}
    if current_app.config['STATISTICS_SHOW_CHARTS']:
        chart_data = prepare_chart_data(sets_by_year_stats, purchases_by_year_stats)

    # Get filter parameters for clickable statistics
    filter_type = request.args.get('filter_type')
    filter_value = request.args.get('filter_value')

    # If a filter is applied, redirect to sets page with appropriate filters
    if filter_type and filter_value:
        return redirect_to_filtered_sets(filter_type, filter_value)

    return render_template(
        'statistics.html',
        overview=overview_stats,
        theme_statistics=theme_stats,
        storage_statistics=storage_stats,
        purchase_location_statistics=purchase_location_stats,
        financial_summary=financial_summary,
        collection_summary=collection_summary,
        sets_by_year_statistics=sets_by_year_stats,
        purchases_by_year_statistics=purchases_by_year_stats,
        year_summary=year_summary,
        chart_data=chart_data,
        title="Statistics Overview"
    )


def redirect_to_filtered_sets(filter_type: str, filter_value: str) -> Response:
    """Redirect to sets page with appropriate filters based on statistics click"""

    # Map filter types to sets page parameters
    filter_mapping = {
        'theme': {'theme': filter_value},
        'storage': {'storage': filter_value},
        'purchase_location': {'purchase_location': filter_value},
        'has_price': {'has_price': '1'} if filter_value == '1' else {},
        'missing_parts': {'status': 'has-missing'},
        'damaged_parts': {'status': 'has-damaged'},
        'has_storage': {'status': 'has-storage'},
        'no_storage': {'status': '-has-storage'},
    }

    # Get the appropriate filter parameters
    filter_params = filter_mapping.get(filter_type, {})

    if filter_params:
        return redirect(url_for('set.list', **filter_params))
    else:
        # Default fallback to sets page
        return redirect(url_for('set.list'))


@statistics_page.route('/themes', methods=['GET'])
@exception_handler(__file__)
def themes() -> str:
    """Detailed theme statistics page"""

    stats = BrickStatistics()
    theme_stats = stats.get_theme_statistics()

    return render_template(
        'statistics_themes.html',
        theme_statistics=theme_stats,
        title="Theme Statistics"
    )


@statistics_page.route('/storage', methods=['GET'])
@exception_handler(__file__)
def storage() -> str:
    """Detailed storage statistics page"""

    stats = BrickStatistics()
    storage_stats = stats.get_storage_statistics()

    return render_template(
        'statistics_storage.html',
        storage_statistics=storage_stats,
        title="Storage Statistics"
    )


@statistics_page.route('/purchase-locations', methods=['GET'])
@exception_handler(__file__)
def purchase_locations() -> str:
    """Detailed purchase location statistics page"""

    stats = BrickStatistics()
    purchase_stats = stats.get_purchase_location_statistics()

    return render_template(
        'statistics_purchase_locations.html',
        purchase_location_statistics=purchase_stats,
        title="Purchase Location Statistics"
    )


def prepare_chart_data(sets_by_year_stats, purchases_by_year_stats):
    """Prepare data for Chart.js visualization"""
    import json

    # Get all years from both datasets
    all_years = set()

    # Add years from sets by year
    if sets_by_year_stats:
        for year_stat in sets_by_year_stats:
            if 'year' in year_stat:
                all_years.add(year_stat['year'])

    # Add years from purchases by year
    if purchases_by_year_stats:
        for year_stat in purchases_by_year_stats:
            if 'purchase_year' in year_stat:
                all_years.add(int(year_stat['purchase_year']))

    # Create sorted list of years
    years = sorted(list(all_years))

    # Initialize data arrays
    sets_data = []
    parts_data = []
    minifigs_data = []

    # Create lookup dictionaries for quick access
    sets_by_year_lookup = {}
    if sets_by_year_stats:
        for year_stat in sets_by_year_stats:
            if 'year' in year_stat:
                sets_by_year_lookup[year_stat['year']] = year_stat

    # Fill data arrays
    for year in years:
        # Get sets and parts data from sets_by_year
        year_data = sets_by_year_lookup.get(year)
        if year_data:
            sets_data.append(year_data.get('total_sets', 0))
            parts_data.append(year_data.get('total_parts', 0))
            # Use actual minifigure count from the database
            minifigs_data.append(year_data.get('total_minifigures', 0))
        else:
            sets_data.append(0)
            parts_data.append(0)
            minifigs_data.append(0)

    return {
        'years': json.dumps(years),
        'sets_data': json.dumps(sets_data),
        'parts_data': json.dumps(parts_data),
        'minifigs_data': json.dumps(minifigs_data)
    }