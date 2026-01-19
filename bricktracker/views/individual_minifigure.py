import logging
from functools import wraps

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from .exceptions import exception_handler
from ..individual_minifigure import IndividualMinifigure
from ..individual_minifigure_list import IndividualMinifigureList
from ..part import BrickPart
from ..set_list import set_metadata_lists
from ..set_owner_list import BrickSetOwnerList
from ..set_tag_list import BrickSetTagList
from ..set_storage_list import BrickSetStorageList
from ..set_purchase_location_list import BrickSetPurchaseLocationList
from ..sql import BrickSQL

logger = logging.getLogger(__name__)

individual_minifigure_page = Blueprint('individual_minifigure', __name__, url_prefix='/individual-minifigures')


def require_individual_minifigures_write(f):
    """Decorator to block write operations (add/update/delete) when individual minifigures are disabled.
    This prevents adding new minifigures but allows viewing existing ones."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('DISABLE_INDIVIDUAL_MINIFIGURES', False):
            abort(404)
        return f(*args, **kwargs)
    return decorated_function


# List all individual minifigures
@individual_minifigure_page.route('/')
@exception_handler(__file__)
def list() -> str:
    minifigures = IndividualMinifigureList().all()

    return render_template(
        'individual_minifigures.html',
        minifigures=minifigures,
        **set_metadata_lists(as_class=True)
    )


# Individual minifigure instance details/edit
@individual_minifigure_page.route('/<id>')
@exception_handler(__file__)
def details(*, id: str) -> str:
    item = IndividualMinifigure().select_by_id(id)

    writes_disabled = current_app.config.get('DISABLE_INDIVIDUAL_MINIFIGURES', False)

    return render_template(
        'individual_minifigure/details.html',
        item=item,
        writes_disabled=writes_disabled,
        **set_metadata_lists(as_class=True)
    )


# Update individual minifigure instance
@individual_minifigure_page.route('/<id>/update', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
def update(*, id: str):
    item = IndividualMinifigure().select_by_id(id)

    # Update basic fields
    item.fields.quantity = int(request.form.get('quantity', 1))
    item.fields.description = request.form.get('description', '')
    item.fields.storage = request.form.get('storage') or None
    item.fields.purchase_location = request.form.get('purchase_location') or None
    item.fields.purchase_date = request.form.get('purchase_date') or None
    item.fields.purchase_price = request.form.get('purchase_price') or None

    # Update the individual minifigure
    from ..sql import BrickSQL
    BrickSQL().execute(
        'individual_minifigure/update',
        parameters={
            'id': item.fields.id,
            'quantity': item.fields.quantity,
            'description': item.fields.description,
            'storage': item.fields.storage,
            'purchase_location': item.fields.purchase_location,
            'purchase_date': item.fields.purchase_date,
            'purchase_price': item.fields.purchase_price,
        },
        commit=False,
    )

    # Update owners
    owners = request.form.getlist('owners')
    for owner in BrickSetOwnerList.list():
        owner.update_individual_minifigure_state(item, state=(owner.fields.id in owners))

    # Update tags
    tags = request.form.getlist('tags')
    for tag in BrickSetTagList.list():
        tag.update_individual_minifigure_state(item, state=(tag.fields.id in tags))

    BrickSQL().commit()

    return redirect(url_for('individual_minifigure.details', id=id))


# Update quantity
@individual_minifigure_page.route('/<id>/update/quantity', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
@login_required
def update_quantity(*, id: str):
    item = IndividualMinifigure().select_by_id(id)
    item.fields.quantity = int(request.json.get('value', 1))

    BrickSQL().execute_and_commit(
        'individual_minifigure/update',
        parameters={
            'id': item.fields.id,
            'quantity': item.fields.quantity,
            'description': item.fields.description,
            'storage': item.fields.storage,
            'purchase_location': item.fields.purchase_location if hasattr(item.fields, 'purchase_location') else None,
            'purchase_date': item.fields.purchase_date if hasattr(item.fields, 'purchase_date') else None,
            'purchase_price': item.fields.purchase_price if hasattr(item.fields, 'purchase_price') else None,
        }
    )

    return jsonify({'success': True})


# Update description
@individual_minifigure_page.route('/<id>/update/description', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
@login_required
def update_description(*, id: str):
    item = IndividualMinifigure().select_by_id(id)
    item.fields.description = request.json.get('value', '')

    BrickSQL().execute_and_commit(
        'individual_minifigure/update',
        parameters={
            'id': item.fields.id,
            'quantity': item.fields.quantity,
            'description': item.fields.description,
            'storage': item.fields.storage,
            'purchase_location': item.fields.purchase_location if hasattr(item.fields, 'purchase_location') else None,
            'purchase_date': item.fields.purchase_date if hasattr(item.fields, 'purchase_date') else None,
            'purchase_price': item.fields.purchase_price if hasattr(item.fields, 'purchase_price') else None,
        }
    )

    return jsonify({'success': True})


# Update owner
@individual_minifigure_page.route('/<id>/update/owner/<metadata_id>', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
@login_required
def update_owner(*, id: str, metadata_id: str):
    item = IndividualMinifigure().select_by_id(id)
    owner = BrickSetOwnerList.get(metadata_id)
    owner.update_individual_minifigure_state(item, json=request.json)

    return jsonify({'success': True})


# Update tag
@individual_minifigure_page.route('/<id>/update/tag/<metadata_id>', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
@login_required
def update_tag(*, id: str, metadata_id: str):
    item = IndividualMinifigure().select_by_id(id)
    tag = BrickSetTagList.get(metadata_id)
    tag.update_individual_minifigure_state(item, json=request.json)

    return jsonify({'success': True})


# Update status
@individual_minifigure_page.route('/<id>/update/status/<metadata_id>', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
@login_required
def update_status(*, id: str, metadata_id: str):
    item = IndividualMinifigure().select_by_id(id)
    from ..set_status_list import BrickSetStatusList
    status = BrickSetStatusList.get(metadata_id)
    status.update_individual_minifigure_state(item, json=request.json)

    return jsonify({'success': True})


# Update storage
@individual_minifigure_page.route('/<id>/update/storage', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
@login_required
def update_storage(*, id: str):
    item = IndividualMinifigure().select_by_id(id)
    storage_id = request.json.get('value')

    BrickSQL().execute_and_commit(
        'individual_minifigure/update',
        parameters={
            'id': item.fields.id,
            'quantity': item.fields.quantity,
            'description': item.fields.description,
            'storage': storage_id if storage_id else None,
            'purchase_location': item.fields.purchase_location if hasattr(item.fields, 'purchase_location') else None,
            'purchase_date': item.fields.purchase_date if hasattr(item.fields, 'purchase_date') else None,
            'purchase_price': item.fields.purchase_price if hasattr(item.fields, 'purchase_price') else None,
        }
    )

    return jsonify({'success': True})


# Update purchase location
@individual_minifigure_page.route('/<id>/update/purchase_location', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
@login_required
def update_purchase_location(*, id: str):
    item = IndividualMinifigure().select_by_id(id)
    location_id = request.json.get('value')

    BrickSQL().execute_and_commit(
        'individual_minifigure/update',
        parameters={
            'id': item.fields.id,
            'quantity': item.fields.quantity,
            'description': item.fields.description,
            'storage': item.fields.storage,
            'purchase_location': location_id if location_id else None,
            'purchase_date': item.fields.purchase_date if hasattr(item.fields, 'purchase_date') else None,
            'purchase_price': item.fields.purchase_price if hasattr(item.fields, 'purchase_price') else None,
        }
    )

    return jsonify({'success': True})


# Update purchase date
@individual_minifigure_page.route('/<id>/update/purchase_date', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
@login_required
def update_purchase_date(*, id: str):
    from datetime import datetime

    item = IndividualMinifigure().select_by_id(id)
    purchase_date_str = request.json.get('value')

    # Convert date string to Unix timestamp (same as sets)
    purchase_date = None
    if purchase_date_str and purchase_date_str != '':
        try:
            purchase_date = datetime.strptime(purchase_date_str, '%Y/%m/%d').timestamp()
        except ValueError as e:
            logger.error('Invalid date format: {date}'.format(date=purchase_date_str))
            return jsonify({'error': '{date} is not a valid date'.format(date=purchase_date_str)}), 400

    BrickSQL().execute_and_commit(
        'individual_minifigure/update',
        parameters={
            'id': item.fields.id,
            'quantity': item.fields.quantity,
            'description': item.fields.description,
            'storage': item.fields.storage,
            'purchase_location': item.fields.purchase_location if hasattr(item.fields, 'purchase_location') else None,
            'purchase_date': purchase_date,
            'purchase_price': item.fields.purchase_price if hasattr(item.fields, 'purchase_price') else None,
        }
    )

    logger.info('Updated individual minifigure {id} purchase_date to: {date}'.format(
        id=id,
        date=purchase_date
    ))
    return jsonify({'success': True})


# Update purchase price
@individual_minifigure_page.route('/<id>/update/purchase_price', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
@login_required
def update_purchase_price(*, id: str):
    item = IndividualMinifigure().select_by_id(id)
    purchase_price = request.json.get('value')

    BrickSQL().execute_and_commit(
        'individual_minifigure/update',
        parameters={
            'id': item.fields.id,
            'quantity': item.fields.quantity,
            'description': item.fields.description,
            'storage': item.fields.storage,
            'purchase_location': item.fields.purchase_location if hasattr(item.fields, 'purchase_location') else None,
            'purchase_date': item.fields.purchase_date if hasattr(item.fields, 'purchase_date') else None,
            'purchase_price': purchase_price if purchase_price else None,
        }
    )

    return jsonify({'success': True})


# Update problematic pieces of an individual minifigure
@individual_minifigure_page.route('/<id>/parts/<part>/<int:color>/<int:spare>/<problem>', methods=['POST'])
@exception_handler(__file__, json=True)
@require_individual_minifigures_write
@login_required
def problem_part(
    *,
    id: str,
    part: str,
    color: int,
    spare: int,
    problem: str,
) -> Response:
    minifigure = IndividualMinifigure().select_by_id(id)

    brickpart = BrickPart().select_specific_individual_minifigure(
        minifigure,
        part,
        color,
        spare,
    )

    amount = brickpart.update_problem_individual_minifigure(problem, request.json)

    # Info
    logger.info('Individual minifigure {figure} ({id}): updated part ({part} color: {color}, spare: {spare}) {problem} count to {amount}'.format(
        figure=minifigure.fields.figure,
        id=minifigure.fields.id,
        part=brickpart.fields.part,
        color=brickpart.fields.color,
        spare=brickpart.fields.spare,
        problem=problem,
        amount=amount
    ))

    return jsonify({problem: amount})


# Update checked state of parts
@individual_minifigure_page.route('/<id>/parts/<part>/<int:color>/<int:spare>/checked', methods=['POST'])
@exception_handler(__file__, json=True)
@require_individual_minifigures_write
@login_required
def checked_part(
    *,
    id: str,
    part: str,
    color: int,
    spare: int,
) -> Response:
    minifigure = IndividualMinifigure().select_by_id(id)

    brickpart = BrickPart().select_specific_individual_minifigure(
        minifigure,
        part,
        color,
        spare,
    )

    checked = brickpart.update_checked_individual_minifigure(request.json)

    # Info
    logger.info('Individual minifigure {figure} ({id}): updated part ({part} color: {color}, spare: {spare}) checked state to {checked}'.format(
        figure=minifigure.fields.figure,
        id=minifigure.fields.id,
        part=brickpart.fields.part,
        color=brickpart.fields.color,
        spare=brickpart.fields.spare,
        checked=checked
    ))

    return jsonify({'checked': checked})


# Delete individual minifigure instance
@individual_minifigure_page.route('/<id>/delete', methods=['POST'])
@exception_handler(__file__)
@require_individual_minifigures_write
@login_required
def delete(*, id: str):
    item = IndividualMinifigure().select_by_id(id)
    figure = item.fields.figure
    item.delete()

    return redirect(url_for('minifigure.details', figure=figure))
