from flask import Blueprint, current_app, render_template, request

from .exceptions import exception_handler
from ..individual_part_list import IndividualPartList
from ..individual_part_lot_list import IndividualPartLotList
from ..metadata_list import custom_field_filters_from_request
from ..minifigure_list import BrickMinifigureList
from ..pagination_helper import get_pagination_config, build_pagination_context, get_request_params
from ..part import BrickPart
from ..part_list import BrickPartList, known_metadata_id
from ..set_custom_field_list import BrickSetCustomFieldList
from ..set_list import BrickSetList, set_metadata_lists
from ..set_owner_list import BrickSetOwnerList
from ..set_status_list import BrickSetStatusList
from ..set_storage_list import BrickSetStorageList
from ..set_tag_list import BrickSetTagList
from ..sql import BrickSQL
from ..theme_list import BrickThemeList

part_page = Blueprint('part', __name__, url_prefix='/parts')


# Read the seven filters off the query string. owner, tag and status end up as SQL
# column names, so they are checked against the ids we know about first. The rest are
# bound as parameters, so they can go through as they are.
def filters_from_request(
    owners: list,
    statuses: list,
    tags: list,
    /,
) -> dict[str, str | None]:
    return {
        'owner_id': known_metadata_id(
            request.args.get('owner'),
            {owner.fields.id for owner in owners},
        ),
        'color_id': request.args.get('color', 'all'),
        'theme_id': request.args.get('theme', 'all'),
        'year': request.args.get('year', 'all'),
        'storage_id': request.args.get('storage', 'all'),
        'tag_id': known_metadata_id(
            request.args.get('tag'),
            {tag.fields.id for tag in tags},
        ),
        'status_id': known_metadata_id(
            request.args.get('status'),
            {status.fields.id for status in statuses},
        ),
    }


# Options for the colour, theme and year dropdowns. They are derived from the parts
# on the page, so they narrow down as the owner filter narrows.
def filter_options(
    owner_id: str | None,
    /,
    *,
    problem_only: bool = False,
) -> dict[str, list]:
    context = {}
    if problem_only:
        context['problem_only'] = True

    # ponytail: a negated owner would give the options of the owner being excluded,
    # so it just does not narrow the lists. Fine for a dropdown.
    if owner_id and not owner_id.startswith('-'):
        context['owner_id'] = owner_id

    theme_list = BrickThemeList()
    themes = []
    for theme_data in BrickSQL().fetchall('part/themes/list', **context):
        theme = theme_list.get(theme_data['theme_id'])
        themes.append({
            'theme_id': theme_data['theme_id'],
            'theme_name': theme.name if theme else 'Theme {id}'.format(
                id=theme_data['theme_id'],
            ),
        })

    return {
        'colors': BrickSQL().fetchall('part/colors/list', **context),
        'themes': themes,
        'years': BrickSQL().fetchall('part/years/list', **context),
    }


# Everything both parts pages need to render. They only differ by problem_only and
# the template, so the filter plumbing lives here once.
def parts_page_context(*, problem_only: bool) -> dict:
    owners = BrickSetOwnerList.list()
    statuses = BrickSetStatusList.list(all=True)
    tags = BrickSetTagList.list()
    storages = BrickSetStorageList.list()
    custom_fields = BrickSetCustomFieldList.list()

    filters = filters_from_request(owners, statuses, tags)
    individuals_filter = request.args.get('individuals', 'all')
    custom_field_filters = custom_field_filters_from_request(
        request.args,
        custom_fields,
    )
    search_query, sort_field, sort_order, page = get_request_params()

    per_page, is_mobile = get_pagination_config(
        'problems' if problem_only else 'parts'
    )
    use_pagination = per_page > 0

    parts = BrickPartList()
    if use_pagination:
        parts, total_count = parts.paginated_filtered(
            problem_only=problem_only,
            individuals_filter=individuals_filter,
            search_query=search_query,
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_order=sort_order,
            custom_field_filters=custom_field_filters,
            **filters
        )
        pagination = build_pagination_context(
            page, per_page, total_count, is_mobile
        )
    else:
        parts = parts.filtered(
            problem_only=problem_only,
            individuals_filter=individuals_filter,
            custom_field_filters=custom_field_filters,
            **filters
        )
        pagination = None

    # Distinct values already in use for each custom field, for its filter dropdown
    custom_field_values = {
        field.fields.id: field.distinct_values()
        for field in custom_fields
    }

    return {
        'table_collection': parts,
        'pagination': pagination,
        'use_pagination': use_pagination,
        'search_query': search_query,
        'sort_field': sort_field,
        'sort_order': sort_order,
        'current_sort': sort_field,
        'current_order': sort_order,
        'owners': owners,
        'storages': storages,
        'tags': tags,
        'statuses': statuses,
        'custom_fields': custom_fields,
        'custom_field_values': custom_field_values,
        'selected_custom_fields': custom_field_filters,
        'selected_owner': request.args.get('owner', 'all'),
        'selected_color': filters['color_id'],
        'selected_theme': filters['theme_id'],
        'selected_year': filters['year'],
        'selected_storage': filters['storage_id'],
        'selected_tag': request.args.get('tag', 'all'),
        'selected_status': request.args.get('status', 'all'),
        'selected_individuals': individuals_filter,
        **filter_options(filters['owner_id'], problem_only=problem_only),
    }


# Index
@part_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'parts.html',
        **parts_page_context(problem_only=False)
    )


# Problem
@part_page.route('/problem', methods=['GET'])
@exception_handler(__file__)
def problem() -> str:
    return render_template(
        'problem.html',
        **parts_page_context(problem_only=True)
    )


# Part details
@part_page.route('/<part>/<int:color>/details', methods=['GET'])  # noqa: E501
@exception_handler(__file__)
def details(*, part: str, color: int) -> str:
    brickpart = BrickPart().select_generic(part, color)

    writes_disabled = current_app.config.get('DISABLE_INDIVIDUAL_PARTS', False)

    return render_template(
        'part.html',
        item=brickpart,
        sets_using=BrickSetList().using_part(
            part,
            color
        ),
        sets_missing=BrickSetList().missing_part(
            part,
            color
        ),
        sets_damaged=BrickSetList().damaged_part(
            part,
            color
        ),
        minifigures_using=BrickMinifigureList().using_part(
            part,
            color
        ),
        minifigures_missing=BrickMinifigureList().missing_part(
            part,
            color
        ),
        minifigures_damaged=BrickMinifigureList().damaged_part(
            part,
            color
        ),
        different_color=BrickPartList().with_different_color(brickpart),
        similar_prints=BrickPartList().from_print(brickpart),
        individual_parts=IndividualPartList().by_part_and_color(part, color),
        individual_lots=IndividualPartLotList().by_part_and_color(part, color),
        writes_disabled=writes_disabled,
        **set_metadata_lists(as_class=True)
    )
