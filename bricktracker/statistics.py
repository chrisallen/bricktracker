"""
Statistics module for BrickTracker
Provides statistics and analytics functionality
"""

import logging
from typing import Any

from .sql import BrickSQL
from .theme_list import BrickThemeList

logger = logging.getLogger(__name__)


class BrickStatistics:
    """Main statistics class providing overview and detailed statistics"""

    def __init__(self):
        self.sql = BrickSQL()

    def get_overview(self) -> dict[str, Any]:
        """Get overview statistics"""
        result = self.sql.fetchone('statistics/overview')
        if result:
            return dict(result)
        return {}

    def get_theme_statistics(self) -> list[dict[str, Any]]:
        """Get statistics grouped by theme with theme names"""
        results = self.sql.fetchall('statistics/themes')

        # Load theme list to get theme names
        theme_list = BrickThemeList()

        statistics = []
        for row in results:
            stat = dict(row)
            # Add theme name from theme list
            theme = theme_list.get(stat['theme_id'])
            stat['theme_name'] = theme.name if theme else f"Theme {stat['theme_id']}"
            statistics.append(stat)

        return statistics

    def get_storage_statistics(self) -> list[dict[str, Any]]:
        """Get statistics grouped by storage location"""
        results = self.sql.fetchall('statistics/storage')
        return [dict(row) for row in results]

    def get_purchase_location_statistics(self) -> list[dict[str, Any]]:
        """Get statistics grouped by purchase location"""
        results = self.sql.fetchall('statistics/purchase_locations')
        return [dict(row) for row in results]

    def get_financial_summary(self) -> dict[str, Any]:
        """Get financial summary from overview statistics (includes all item types)"""
        overview = self.get_overview()
        return {
            'total_cost': overview.get('combined_total_cost') or 0,
            'average_cost': overview.get('combined_average_cost') or 0,
            'minimum_cost': overview.get('combined_minimum_cost') or 0,
            'maximum_cost': overview.get('combined_maximum_cost') or 0,
            'items_with_price': overview.get('total_items_with_price') or 0,
            'sets_with_price': overview.get('sets_with_price') or 0,
            'total_sets': overview.get('total_sets') or 0,
            'percentage_with_price': round(
                ((overview.get('total_items_with_price') or 0) / max((overview.get('total_sets') or 0), 1)) * 100, 1
            )
        }

    def get_collection_summary(self) -> dict[str, Any]:
        """Get collection summary from overview statistics"""
        overview = self.get_overview()
        return {
            'total_sets': overview.get('total_sets') or 0,
            'unique_sets': overview.get('unique_sets') or 0,
            'total_parts_count': overview.get('total_parts_count') or 0,
            'unique_parts': overview.get('unique_parts') or 0,
            'total_minifigures_count': overview.get('total_minifigures_count') or 0,
            'unique_minifigures': overview.get('unique_minifigures') or 0,
            'total_missing_parts': overview.get('total_missing_parts') or 0,
            'total_damaged_parts': overview.get('total_damaged_parts') or 0,
            'storage_locations_used': overview.get('storage_locations_used') or 0,
            'purchase_locations_used': overview.get('purchase_locations_used') or 0
        }

    def get_sets_by_year_statistics(self) -> list[dict[str, Any]]:
        """Get statistics grouped by LEGO set release year"""
        results = self.sql.fetchall('statistics/sets_by_year')
        return [dict(row) for row in results]

    def get_purchases_by_year_statistics(self) -> list[dict[str, Any]]:
        """Get statistics grouped by purchase year"""
        results = self.sql.fetchall('statistics/purchases_by_year')
        return [dict(row) for row in results]

    def get_year_summary(self) -> dict[str, Any]:
        """Get year-based summary statistics"""
        sets_by_year = self.get_sets_by_year_statistics()
        purchases_by_year = self.get_purchases_by_year_statistics()

        # Calculate summary metrics
        years_represented = len(sets_by_year)
        years_with_purchases = len(purchases_by_year)

        # Find peak year for collection (by set count)
        peak_collection_year = None
        max_sets_in_year = 0
        if sets_by_year:
            peak_year_data = max(sets_by_year, key=lambda x: x.get('total_sets') or 0)
            peak_collection_year = peak_year_data.get('year')
            max_sets_in_year = peak_year_data.get('total_sets') or 0

        # Find peak spending year
        peak_spending_year = None
        max_spending = 0
        if purchases_by_year:
            spending_years = [y for y in purchases_by_year if y.get('total_spent')]
            if spending_years:
                peak_spending_data = max(spending_years, key=lambda x: x.get('total_spent') or 0)
                peak_spending_year = peak_spending_data.get('purchase_year')
                max_spending = peak_spending_data.get('total_spent') or 0

        return {
            'years_represented': years_represented,
            'years_with_purchases': years_with_purchases,
            'peak_collection_year': peak_collection_year,
            'max_sets_in_year': max_sets_in_year,
            'peak_spending_year': peak_spending_year,
            'max_spending': max_spending,
            'oldest_set_year': min([y['year'] for y in sets_by_year]) if sets_by_year else None,
            'newest_set_year': max([y['year'] for y in sets_by_year]) if sets_by_year else None
        }