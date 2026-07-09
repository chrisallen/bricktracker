import logging
import os

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    redirect,
    request,
    url_for,
)
from flask_login import login_required
from werkzeug.wrappers.response import Response

from .exceptions import exception_handler
from ..exceptions import ErrorException
from ..minifigure import BrickMinifigure
from ..pagination_helper import get_pagination_config, build_pagination_context, get_request_params
from ..part import BrickPart
from ..rebrickable_image import RebrickableImage
from ..rebrickable_set import RebrickableSet
from ..set import BrickSet
from ..sidecar import BrickSidecar
from ..sidecar_set import summarize as sidecar_summarize
from ..set_custom_field_list import BrickSetCustomFieldList
from ..set_list import BrickSetList, set_metadata_lists
from ..set_owner_list import BrickSetOwnerList
from ..set_purchase_location_list import BrickSetPurchaseLocationList
from ..set_status_list import BrickSetStatusList
from ..set_storage_list import BrickSetStorageList
from ..set_tag_list import BrickSetTagList
from ..socket import MESSAGES
from ..sql import BrickSQL

logger = logging.getLogger(__name__)

set_page = Blueprint('set', __name__, url_prefix='/sets')


# List of all sets
@set_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    # Get filter parameters from request
    search_query, sort_field, sort_order, page = get_request_params()

    # Get filter parameters
    status_filter = request.args.get('status')
    theme_filter = request.args.get('theme')
    owner_filter = request.args.get('owner')
    purchase_location_filter = request.args.get('purchase_location')
    storage_filter = request.args.get('storage')
    tag_filter = request.args.get('tag')
    year_filter = request.args.get('year')
    duplicate_filter = request.args.get('duplicate', '').lower() == 'true'

    # Get pagination configuration
    per_page, is_mobile = get_pagination_config('sets')
    use_pagination = per_page > 0

    if use_pagination:
        # PAGINATION MODE - Server-side pagination with search and filters
        sets, total_count = BrickSetList().all_filtered_paginated(
            search_query=search_query,
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_order=sort_order,
            status_filter=status_filter,
            theme_filter=theme_filter,
            owner_filter=owner_filter,
            purchase_location_filter=purchase_location_filter,
            storage_filter=storage_filter,
            tag_filter=tag_filter,
            year_filter=year_filter,
            duplicate_filter=duplicate_filter,
            use_consolidated=current_app.config['SETS_CONSOLIDATION']
        )

        pagination_context = build_pagination_context(page, per_page, total_count, is_mobile)
    else:
        # ORIGINAL MODE - Single page with all data for client-side search
        if current_app.config['SETS_CONSOLIDATION']:
            sets = BrickSetList().all_consolidated()
        else:
            sets = BrickSetList().all()
        pagination_context = None

    # Convert theme ID to theme name for dropdown display if needed
    display_theme_filter = theme_filter
    if theme_filter and theme_filter.isdigit():
        # Theme filter is an ID, convert to name for dropdown
        # Create a fresh BrickSetList instance for theme conversion
        converter = BrickSetList()
        theme_name = converter._theme_id_to_name(theme_filter)
        if theme_name:
            display_theme_filter = theme_name

    template_context = {
        'collection': sets,
        'search_query': search_query,
        'use_pagination': use_pagination,
        'current_sort': sort_field,
        'current_order': sort_order,
        'current_status_filter': status_filter,
        'current_theme_filter': display_theme_filter,
        'current_owner_filter': owner_filter,
        'current_purchase_location_filter': purchase_location_filter,
        'current_storage_filter': storage_filter,
        'current_tag_filter': tag_filter,
        'current_year_filter': year_filter,
        'current_duplicate_filter': duplicate_filter,
        'brickset_statuses': BrickSetStatusList.list(),
        **set_metadata_lists(as_class=True)
    }

    if pagination_context:
        template_context['pagination'] = pagination_context

    return render_template('sets.html', **template_context)


# Change the value of purchase date
@set_page.route('/<id>/purchase_date', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_purchase_date(*, id: str) -> Response:
    brickset = BrickSet().select_light(id)

    value = brickset.update_purchase_date(request.json)

    return jsonify({'value': value})


# Change the value of purchase location
@set_page.route('/<id>/purchase_location', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_purchase_location(*, id: str) -> Response:
    brickset = BrickSet().select_light(id)
    purchase_location = BrickSetPurchaseLocationList.get(
        request.json.get('value', ''),  # type: ignore
        allow_none=True
    )

    value = purchase_location.update_set_value(
        brickset,
        value=purchase_location.fields.id
    )

    return jsonify({'value': value})


# Change the value of purchase price
@set_page.route('/<id>/purchase_price', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_purchase_price(*, id: str) -> Response:
    brickset = BrickSet().select_light(id)

    value = brickset.update_purchase_price(request.json)

    return jsonify({'value': value})


# Change the value of description
@set_page.route('/<id>/description', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_description(*, id: str) -> Response:
    brickset = BrickSet().select_light(id)

    value = brickset.update_description(request.json)

    return jsonify({'value': value})


# Change the state of a owner
@set_page.route('/<id>/owner/<metadata_id>', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_owner(*, id: str, metadata_id: str) -> Response:
    brickset = BrickSet().select_light(id)
    owner = BrickSetOwnerList.get(metadata_id)

    state = owner.update_set_state(brickset, json=request.json)

    return jsonify({'value': state})


# Change the state of a status
@set_page.route('/<id>/status/<metadata_id>', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_status(*, id: str, metadata_id: str) -> Response:
    brickset = BrickSet().select_light(id)
    status = BrickSetStatusList.get(metadata_id)

    state = status.update_set_state(brickset, json=request.json)

    return jsonify({'value': state})


# Change the value of storage
@set_page.route('/<id>/storage', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_storage(*, id: str) -> Response:
    brickset = BrickSet().select_light(id)
    storage = BrickSetStorageList.get(
        request.json.get('value', ''),  # type: ignore
        allow_none=True
    )

    value = storage.update_set_value(brickset, value=storage.fields.id)

    return jsonify({'value': value})


# Change the state of a tag
@set_page.route('/<id>/tag/<metadata_id>', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_tag(*, id: str, metadata_id: str) -> Response:
    brickset = BrickSet().select_light(id)
    tag = BrickSetTagList.get(metadata_id)

    state = tag.update_set_state(brickset, json=request.json)

    return jsonify({'value': state})


# Change the value of a custom field
@set_page.route('/<id>/custom_field/<metadata_id>', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_custom_field(*, id: str, metadata_id: str) -> Response:
    brickset = BrickSet().select_light(id)
    custom_field = BrickSetCustomFieldList.get(metadata_id)

    value = custom_field.update_value(brickset, json=request.json)

    return jsonify({'value': value})


# Mass-edit metadata across several selected sets in one request. Only the
# fields the user actually touched are present in "changes"; tri-state booleans
# arrive as explicit true/false, value fields as a string ('' clears).
@set_page.route('/bulk/edit', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def bulk_edit() -> Response:
    payload = request.json or {}
    set_ids = payload.get('set_ids', [])
    changes = payload.get('changes', {})

    if not set_ids:
        raise ErrorException('No sets were selected')

    tags = changes.get('tags', {})
    statuses = changes.get('statuses', {})
    owners = changes.get('owners', {})
    custom_fields = changes.get('custom_fields', {})

    has_storage = 'storage' in changes
    has_purchase_location = 'purchase_location' in changes
    has_purchase_date = 'purchase_date' in changes
    has_purchase_price = 'purchase_price' in changes
    has_description = 'description' in changes

    for set_id in set_ids:
        brickset = BrickSet().select_light(set_id)

        # Boolean metadata: defer so the batch is grouped (committed below).
        for metadata_id, state in tags.items():
            BrickSetTagList.get(metadata_id).update_set_state(
                brickset, state=state, commit=False
            )
        for metadata_id, state in statuses.items():
            BrickSetStatusList.get(metadata_id).update_set_state(
                brickset, state=state, commit=False
            )
        for metadata_id, state in owners.items():
            BrickSetOwnerList.get(metadata_id).update_set_state(
                brickset, state=state, commit=False
            )

        # Value metadata (each commits on its own).
        if has_storage:
            storage = BrickSetStorageList.get(
                changes.get('storage', ''), allow_none=True
            )
            storage.update_set_value(brickset, value=storage.fields.id)

        if has_purchase_location:
            purchase_location = BrickSetPurchaseLocationList.get(
                changes.get('purchase_location', ''), allow_none=True
            )
            purchase_location.update_set_value(
                brickset, value=purchase_location.fields.id
            )

        if has_purchase_date:
            brickset.update_purchase_date(
                {'value': changes.get('purchase_date', '')}
            )

        if has_purchase_price:
            brickset.update_purchase_price(
                {'value': changes.get('purchase_price', '')}
            )

        if has_description:
            brickset.update_description(
                {'value': changes.get('description', '')}
            )

        for metadata_id, value in custom_fields.items():
            BrickSetCustomFieldList.get(metadata_id).update_value(
                brickset, value=value
            )

    # Flush any deferred boolean updates that did not ride along with a
    # value update's commit.
    BrickSQL().commit()

    logger.info('Bulk edit applied to {count} set(s)'.format(
        count=len(set_ids),
    ))

    return jsonify({'updated': len(set_ids)})


# Ask for deletion of a set
@set_page.route('/<id>/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, id: str) -> str:
    return render_template(
        'set.html',
        delete=True,
        item=BrickSet().select_specific(id),
        error=request.args.get('error'),
        **set_metadata_lists(as_class=True)
    )


# Actually delete of a set
@set_page.route('/<id>/delete', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='set.delete')
def do_delete(*, id: str) -> Response:
    brickset = BrickSet().select_light(id)
    brickset.delete()

    # Info
    logger.info('Set {set} ({id}): deleted'.format(
        set=brickset.fields.set,
        id=brickset.fields.id,
    ))

    return redirect(url_for('set.deleted', id=id))


# Set is deleted
@set_page.route('/<id>/deleted', methods=['GET'])
@login_required
@exception_handler(__file__)
def deleted(*, id: str) -> str:
    return render_template(
        'success.html',
        message='Set "{id}" has been successfuly deleted.'.format(id=id),
    )


# Details of one set
@set_page.route('/<id>/details', methods=['GET'])
@exception_handler(__file__)
def details(*, id: str) -> str:
    # Load the specific set
    item = BrickSet().select_specific(id)

    # Sidecar enrichment + price comparison. Cache-only by default; when
    # SIDECAR_AUTO_FETCH_PRICE is on, the market value is fetched on view
    # (TTL-aware) so the user does not have to press "Fetch value".
    sidecar_summary = sidecar_summarize(
        item.fields.set,
        purchase_price=item.fields.purchase_price,
        fetch_price=current_app.config.get('SIDECAR_AUTO_FETCH_PRICE', False),
    )

    # Check if there are multiple instances of this set
    all_instances = BrickSetList()
    # Load all sets with metadata context for tags, owners, etc.
    filter_context = {
        'owners': BrickSetOwnerList.as_columns(),
        'statuses': BrickSetStatusList.as_columns(),
        'tags': BrickSetTagList.as_columns(),
    }
    all_instances.list(do_theme=True, **filter_context)

    # Find all instances with the same set number
    same_set_instances = [
        record for record in all_instances.records
        if record.fields.set == item.fields.set
    ]

    # If consolidation is enabled and multiple instances exist, show consolidated view
    if current_app.config['SETS_CONSOLIDATION'] and len(same_set_instances) > 1:
        return render_template(
            'set.html',
            item=item,
            all_instances=same_set_instances,
            open_instructions=request.args.get('open_instructions'),
            brickset_statuses=BrickSetStatusList.list(all=True),
            sidecar_summary=sidecar_summary,
            **set_metadata_lists(as_class=True)
        )
    else:
        # Single instance or consolidation disabled, show normal view
        return render_template(
            'set.html',
            item=item,
            open_instructions=request.args.get('open_instructions'),
            brickset_statuses=BrickSetStatusList.list(all=True),
            sidecar_summary=sidecar_summary,
            **set_metadata_lists(as_class=True)
        )


# Update problematic pieces of a set
@set_page.route('/<id>/parts/<part>/<int:color>/<int:spare>/<problem>', defaults={'figure': None}, methods=['POST'])  # noqa: E501
@set_page.route('/<id>/minifigures/<figure>/parts/<part>/<int:color>/<int:spare>/<problem>', methods=['POST'])  # noqa: E501
@login_required
@exception_handler(__file__, json=True)
def problem_part(
    *,
    id: str,
    figure: str | None,
    part: str,
    color: int,
    spare: int,
    problem: str,
) -> Response:
    brickset = BrickSet().select_specific(id)

    if figure is not None:
        brickminifigure = BrickMinifigure().select_specific(brickset, figure)
    else:
        brickminifigure = None

    brickpart = BrickPart().select_specific(
        brickset,
        part,
        color,
        spare,
        minifigure=brickminifigure,
    )

    amount = brickpart.update_problem(problem, request.json)

    # Info
    logger.info('Set {set} ({id}): updated part ({part} color: {color}, spare: {spare}, minifigure: {figure}) {problem} count to {amount}'.format(  # noqa: E501
        set=brickset.fields.set,
        id=brickset.fields.id,
        figure=figure,
        part=brickpart.fields.part,
        color=brickpart.fields.color,
        spare=brickpart.fields.spare,
        problem=problem,
        amount=amount
    ))

    return jsonify({problem: amount})


# Update checked state of parts during walkthrough
@set_page.route('/<id>/parts/<part>/<int:color>/<int:spare>/checked', defaults={'figure': None}, methods=['POST'])  # noqa: E501
@set_page.route('/<id>/minifigures/<figure>/parts/<part>/<int:color>/<int:spare>/checked', methods=['POST'])  # noqa: E501
@login_required
@exception_handler(__file__, json=True)
def checked_part(
    *,
    id: str,
    figure: str | None,
    part: str,
    color: int,
    spare: int,
) -> Response:
    brickset = BrickSet().select_specific(id)

    if figure is not None:
        brickminifigure = BrickMinifigure().select_specific(brickset, figure)
    else:
        brickminifigure = None

    brickpart = BrickPart().select_specific(
        brickset,
        part,
        color,
        spare,
        minifigure=brickminifigure,
    )

    checked = brickpart.update_checked(request.json)

    # Info
    logger.info('Set {set} ({id}): updated part ({part} color: {color}, spare: {spare}, minifigure: {figure}) checked state to {checked}'.format(  # noqa: E501
        set=brickset.fields.set,
        id=brickset.fields.id,
        figure=figure,
        part=brickpart.fields.part,
        color=brickpart.fields.color,
        spare=brickpart.fields.spare,
        checked=checked
    ))

    return jsonify({'checked': checked})


# Refresh a set
@set_page.route('/refresh/<set>/', methods=['GET'])
@set_page.route('/<id>/refresh', methods=['GET'])
@login_required
@exception_handler(__file__)
def refresh(*, id: str | None = None, set: str | None = None) -> str:
    if id is not None:
        item = BrickSet().select_specific(id)
    elif set is not None:
        item = RebrickableSet().select_specific(set)
    else:
        raise ErrorException('Could not load any set to refresh')

    return render_template(
        'refresh.html',
        id=id,
        item=item,
        path=current_app.config['SOCKET_PATH'],
        namespace=current_app.config['SOCKET_NAMESPACE'],
        messages=MESSAGES
    )


# Override the cover image with a sidecar image (box / set art). Best quality
# first: tries the *_large variant, falls back to the normal resolution (which
# BrickLink almost always has where _large is missing).
@set_page.route('/<id>/cover/<image_type>', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='set.details')
def cover_override(*, id: str, image_type: str) -> Response:
    if image_type not in ('box', 'set'):
        raise ErrorException('Unknown cover image type: {type}'.format(
            type=image_type,
        ))

    if not BrickSidecar.enabled():
        raise ErrorException('The sidecar is not configured')

    brickset = BrickSet().select_light(id)
    ref = brickset.fields.set

    # BrickLink box/set covers only reliably exist at normal resolution
    # (the *_large variants are almost always 404), so use the normal image.
    saved = BrickSidecar.save_cover_override(ref, image_type)

    if not saved:
        raise ErrorException(
            'The sidecar has no {type} image for set {ref}'.format(
                type=image_type,
                ref=ref,
            )
        )

    logger.info('Set {ref} ({id}): cover overridden with sidecar {type} art'.format(  # noqa: E501
        ref=ref,
        id=id,
        type=image_type,
    ))

    return redirect(brickset.url())


# Override the cover with one of the Brickset additional images (0-indexed).
@set_page.route('/<id>/cover/additional/<int:index>', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='set.details')
def cover_override_additional(*, id: str, index: int) -> Response:
    if not current_app.config['SIDECAR_ADDITIONAL_IMAGES']:
        raise ErrorException('Additional images are not enabled')

    if not BrickSidecar.enabled():
        raise ErrorException('The sidecar is not configured')

    brickset = BrickSet().select_light(id)
    ref = brickset.fields.set

    saved = BrickSidecar.save_cover_override_from_additional(ref, index)

    if not saved:
        raise ErrorException(
            'The sidecar has no additional image {index} for set {ref}'.format(
                index=index,
                ref=ref,
            )
        )

    logger.info('Set {ref} ({id}): cover overridden with additional image {index}'.format(  # noqa: E501
        ref=ref,
        id=id,
        index=index,
    ))

    return redirect(brickset.url())


# Restore the original Rebrickable cover: use the backup if we made one,
# otherwise delete the local file and re-download from Rebrickable.
@set_page.route('/<id>/cover/restore', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='set.details')
def cover_restore(*, id: str) -> Response:
    brickset = BrickSet().select_specific(id)
    ref = brickset.fields.set

    if not BrickSidecar.restore_cover(ref):
        # No backup to restore: drop the local file and pull from Rebrickable.
        path = BrickSidecar.cover_path(ref)
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass

        RebrickableImage(brickset).download()

    logger.info('Set {ref} ({id}): cover restored to Rebrickable image'.format(
        ref=ref,
        id=id,
    ))

    return redirect(brickset.url())


# Lazily (re)fetch the BrickLink market value for a set and cache it. This is
# the expensive live path, so it only runs on an explicit user action.
@set_page.route('/<id>/value/refresh', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='set.details')
def value_refresh(*, id: str) -> Response:
    if not BrickSidecar.enabled():
        raise ErrorException('The sidecar is not configured')

    brickset = BrickSet().select_light(id)
    ref = brickset.fields.set

    price = BrickSidecar.get_price(ref, refresh=True)

    if price is None:
        raise ErrorException(
            'Could not fetch a market value for set {ref}'.format(ref=ref),
        )

    logger.info('Set {ref} ({id}): market value refreshed'.format(
        ref=ref,
        id=id,
    ))

    return redirect(brickset.url())
