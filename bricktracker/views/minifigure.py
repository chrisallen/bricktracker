from flask import Blueprint, current_app, render_template, request

from .exceptions import exception_handler
from ..individual_minifigure_list import IndividualMinifigureList
from ..metadata_list import custom_field_filters_from_request
from ..minifigure import BrickMinifigure
from ..minifigure_list import BrickMinifigureList
from ..pagination_helper import get_pagination_config, build_pagination_context, get_request_params
from ..part_list import known_metadata_id
from ..set_custom_field_list import BrickSetCustomFieldList
from ..set_list import BrickSetList, set_metadata_lists
from ..set_owner_list import BrickSetOwnerList

minifigure_page = Blueprint('minifigure', __name__, url_prefix='/minifigures')


# Index
@minifigure_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    owners = BrickSetOwnerList.list()
    custom_fields = BrickSetCustomFieldList.list()

    # Get filter parameters from request. owner is interpolated as a column name
    # downstream, so it is checked against the owner ids we already know about first.
    owner_id = known_metadata_id(
        request.args.get('owner', 'all'),
        {owner.fields.id for owner in owners},
    ) or 'all'
    problems_filter = request.args.get('problems', 'all')
    theme_id = request.args.get('theme', 'all')
    year = request.args.get('year', 'all')
    individuals_filter = request.args.get('individuals', 'all')
    custom_field_filters = custom_field_filters_from_request(
        request.args,
        custom_fields,
    )
    search_query, sort_field, sort_order, page = get_request_params()

    # Get pagination configuration
    per_page, is_mobile = get_pagination_config('minifigures')
    use_pagination = per_page > 0

    if use_pagination:
        # PAGINATION MODE - Server-side pagination with search
        minifigures, total_count = BrickMinifigureList().all_filtered_paginated(
            owner_id=owner_id,
            problems_filter=problems_filter,
            theme_id=theme_id,
            year=year,
            individuals_filter=individuals_filter,
            search_query=search_query,
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_order=sort_order,
            custom_field_filters=custom_field_filters,
        )

        pagination_context = build_pagination_context(page, per_page, total_count, is_mobile)
    else:
        # ORIGINAL MODE - Single page with all data for client-side search
        minifigures = BrickMinifigureList().all_filtered(
            owner_id=owner_id,
            problems_filter=problems_filter,
            theme_id=theme_id,
            year=year,
            individuals_filter=individuals_filter,
            custom_field_filters=custom_field_filters,
        )

        pagination_context = None

    # Prepare context for dependent filters. A negated owner would give the options
    # of the owner being excluded, so it just does not narrow the lists (same call
    # parts.py makes).
    filter_context = {}
    if owner_id != 'all' and owner_id and not owner_id.startswith('-'):
        filter_context['owner_id'] = owner_id

    # Get list of themes for filter dropdown
    from ..theme_list import BrickThemeList
    from ..sql import BrickSQL
    theme_list = BrickThemeList()
    themes_data = BrickSQL().fetchall('minifigure/themes/list', **filter_context)
    themes = []
    for theme_data in themes_data:
        theme = theme_list.get(theme_data['theme_id'])
        themes.append({
            'theme_id': theme_data['theme_id'],
            'theme_name': theme.name if theme else f"Theme {theme_data['theme_id']}"
        })

    # Get list of years for filter dropdown
    years = BrickSQL().fetchall('minifigure/years/list', **filter_context)

    # Distinct values already in use for each custom field, for its filter dropdown
    custom_field_values = {
        field.fields.id: field.distinct_values()
        for field in custom_fields
    }

    template_context = {
        'table_collection': minifigures,
        'owners': owners,
        'selected_owner': owner_id,
        'selected_problems': problems_filter,
        'themes': themes,
        'selected_theme': theme_id,
        'years': years,
        'selected_year': year,
        'selected_individuals': individuals_filter,
        'custom_fields': custom_fields,
        'custom_field_values': custom_field_values,
        'selected_custom_fields': custom_field_filters,
        'search_query': search_query,
        'use_pagination': use_pagination,
        'current_sort': sort_field,
        'current_order': sort_order
    }

    if pagination_context:
        template_context['pagination'] = pagination_context

    return render_template('minifigures.html', **template_context)


# Minifigure details
@minifigure_page.route('/<figure>/details')
@exception_handler(__file__)
def details(*, figure: str) -> str:
    writes_disabled = current_app.config.get('DISABLE_INDIVIDUAL_MINIFIGURES', False)

    return render_template(
        'minifigure.html',
        item=BrickMinifigure().select_generic(figure),
        using=BrickSetList().using_minifigure(figure),
        missing=BrickSetList().missing_minifigure(figure),
        damaged=BrickSetList().damaged_minifigure(figure),
        individual_instances=IndividualMinifigureList().instances_by_figure(figure),
        writes_disabled=writes_disabled,
        **set_metadata_lists(as_class=True)
    )
