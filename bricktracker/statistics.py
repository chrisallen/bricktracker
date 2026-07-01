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
            'minimum_cost': float(overview['combined_minimum_cost']) if overview.get('combined_minimum_cost') not in (None, '') else None,
            'maximum_cost': float(overview['combined_maximum_cost']) if overview.get('combined_maximum_cost') not in (None, '') else None,
            'items_with_price': overview.get('total_items_with_price') or 0,
            'sets_with_price': overview.get('sets_with_price') or 0,
            'total_sets': overview.get('total_sets') or 0,
            'total_items': overview.get('total_items') or 0,
            # #156: divide by the matching total of all priceable item types
            # (not total_sets), and clamp to 100% as a safety net.
            'percentage_with_price': min(round(
                ((overview.get('total_items_with_price') or 0) / max((overview.get('total_items') or 0), 1)) * 100, 1
            ), 100.0)
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

    def get_instructions_summary(self) -> dict[str, Any] | None:
        """Instruction coverage across the collection (#154).

        Instructions live on the filesystem (INSTRUCTIONS_FOLDER), not in the
        database, so this intersects the distinct collection set numbers with the
        cached instructions file list. Returns None when instructions are hidden.
        """
        from flask import current_app

        if current_app.config.get('HIDE_SET_INSTRUCTIONS', False):
            return None

        from .instructions_list import BrickInstructionsList

        instructions = BrickInstructionsList()

        rows = self.sql.fetchall('statistics/set_numbers')
        set_numbers = {row['set'] for row in rows}

        with_instructions = sum(
            1 for number in set_numbers if number in instructions.sets
        )
        unique_sets = len(set_numbers)

        return {
            'instruction_files': instructions.sets_total,
            'sets_with_instructions': with_instructions,
            'unique_sets': unique_sets,
            'percentage_with_instructions': min(round(
                (with_instructions / max(unique_sets, 1)) * 100, 1
            ), 100.0),
        }

    def get_sidecar_pricing_summary(self) -> dict[str, Any] | None:
        """Collection-wide paid / retail (MSRP) / BrickLink market comparison.

        Pulls cached metadata + price for the whole collection from the sidecar
        in one bulk call and aggregates in Python (the sidecar is the single
        cache). Returns None when the sidecar is disabled or unreachable.
        """
        from .sidecar import BrickSidecar

        if not BrickSidecar.enabled():
            return None

        try:
            instances = self.sql.fetchall('statistics/sidecar_sets')
        except Exception as exception:
            logger.debug('sidecar pricing summary failed: %s', exception)
            return None

        instances = [dict(row) for row in instances]
        if not instances:
            return None

        refs = list({row['set_ref'] for row in instances if row.get('set_ref')})
        try:
            bulk = BrickSidecar.get_sets_bulk(refs)
        except Exception as exception:
            logger.debug('sidecar bulk fetch failed: %s', exception)
            return None

        def to_number(value: Any) -> float | None:
            try:
                return float(value) if value is not None else None
            except (TypeError, ValueError):
                return None

        data: dict[str, Any] = {
            'total_sets': 0,
            'total_paid': 0.0, 'sets_with_paid': 0,
            'total_msrp': 0.0, 'sets_with_msrp': 0,
            'total_market_new': 0.0, 'sets_with_market': 0,
            'total_market_used': 0.0, 'sets_with_market_used': 0,
            'paid_where_msrp': 0.0, 'msrp_where_paid': 0.0,
            'paid_where_market': 0.0, 'market_where_paid': 0.0,
            'paid_where_market_used': 0.0, 'market_used_where_paid': 0.0,
            'market_currency': None,
        }

        # One row per set instance, mirroring the old per-instance aggregation.
        for row in instances:
            set_data = bulk.get(row.get('set_ref')) or {}
            price_block = set_data.get('bricklink_price') or {}

            paid = to_number(row.get('purchase_price'))
            msrp = BrickSidecar.retail_price(set_data) if set_data else None
            market_new = to_number(price_block.get('new_avg'))
            market_used = to_number(price_block.get('used_avg'))

            data['total_sets'] += 1
            if paid is not None:
                data['total_paid'] += paid
                data['sets_with_paid'] += 1
            if msrp is not None:
                data['total_msrp'] += msrp
                data['sets_with_msrp'] += 1
            if market_new is not None:
                data['total_market_new'] += market_new
                data['sets_with_market'] += 1
            if market_used is not None:
                data['total_market_used'] += market_used
                data['sets_with_market_used'] += 1
            if msrp is not None and paid is not None:
                data['paid_where_msrp'] += paid
                data['msrp_where_paid'] += msrp
            if market_new is not None and paid is not None:
                data['paid_where_market'] += paid
                data['market_where_paid'] += market_new
            if market_used is not None and paid is not None:
                data['paid_where_market_used'] += paid
                data['market_used_where_paid'] += market_used
            if data['market_currency'] is None and price_block.get('currency_code'):
                data['market_currency'] = price_block.get('currency_code')

        def number(key: str) -> float:
            value = data.get(key)
            try:
                return float(value) if value is not None else 0.0
            except (TypeError, ValueError):
                return 0.0

        # Savings vs retail and value change vs paid, computed only across the
        # sets where both sides of the comparison are known.
        data['total_saved_vs_msrp'] = round(
            number('msrp_where_paid') - number('paid_where_msrp'), 2
        )
        data['total_gain_vs_paid'] = round(
            number('market_where_paid') - number('paid_where_market'), 2
        )
        data['total_gain_vs_paid_used'] = round(
            number('market_used_where_paid') - number('paid_where_market_used'), 2
        )
        data['retail_currency'] = BrickSidecar.retail_currency()

        # Currency the user records purchase prices in (may be a symbol such as
        # '$' or 'kr'). Compared against the retail/market ISO codes through the
        # symbol map so '$' vs 'USD' and 'kr' vs 'DKK' are NOT flagged.
        from flask import current_app
        paid_currency = str(
            current_app.config.get('PURCHASE_CURRENCY', '') or ''
        ).strip()
        data['paid_currency'] = paid_currency

        mismatch = False
        if data.get('sets_with_paid'):
            if not BrickSidecar.same_currency(paid_currency, data.get('market_currency')):
                mismatch = True
            if not BrickSidecar.same_currency(paid_currency, data['retail_currency']):
                mismatch = True
        data['currency_mismatch'] = mismatch

        return data

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