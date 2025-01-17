import logging

from flask import (
    Blueprint,
    jsonify,
    render_template,
    redirect,
    request,
    url_for,
)
from flask_login import login_required
from werkzeug.wrappers.response import Response

from .exceptions import exception_handler
from ..minifigure import BrickMinifigure
from ..part import BrickPart
from ..set import BrickSet
from ..set_list import BrickSetList

logger = logging.getLogger(__name__)

set_page = Blueprint('set', __name__, url_prefix='/sets')


# List of all sets
@set_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template('sets.html', collection=BrickSetList().all())


# Change the set checked status of one set
@set_page.route('/<id>/checked', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def set_checked(*, id: str) -> Response:
    state: bool = request.json.get('state', False)  # type: ignore

    brickset = BrickSet().select_specific(id)
    brickset.update_checked('set_check', state)

    # Info
    logger.info('Set {number} ({id}): changed set checked status to {state}'.format(  # noqa: E501
        number=brickset.fields.set_num,
        id=brickset.fields.u_id,
        state=state,
    ))

    return jsonify({'state': state})


# Change the set collected status of one set
@set_page.route('/<id>/collected', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def set_collected(*, id: str) -> Response:
    state: bool = request.json.get('state', False)  # type: ignore

    brickset = BrickSet().select_specific(id)
    brickset.update_checked('set_col', state)

    # Info
    logger.info('Set {number} ({id}): changed set collected status to {state}'.format(  # noqa: E501
        number=brickset.fields.set_num,
        id=brickset.fields.u_id,
        state=state,
    ))

    return jsonify({'state': state})


# Ask for deletion of a set
@set_page.route('/<id>/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, id: str) -> str:
    return render_template(
        'delete.html',
        item=BrickSet().select_specific(id),
        error=request.args.get('error'),
    )


# Actually delete of a set
@set_page.route('/<id>/delete', methods=['POST'])
@exception_handler(__file__, post_redirect='set.delete')
def do_delete(*, id: str) -> Response:
    brickset = BrickSet().select_specific(id)
    brickset.delete()

    # Info
    logger.info('Set {number} ({id}): deleted'.format(
        number=brickset.fields.set_num,
        id=brickset.fields.u_id,
    ))

    return redirect(url_for('set.deleted', id=id))


# Set is deleted
@set_page.route('/<id>/deleted', methods=['GET'])
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
    return render_template(
        'set.html',
        item=BrickSet().select_specific(id),
        open_instructions=request.args.get('open_instructions'),
    )


# Change the minifigures collected status of one set
@set_page.route('/sets/<id>/minifigures/collected', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def minifigures_collected(*, id: str) -> Response:
    state: bool = request.json.get('state', False)  # type: ignore

    brickset = BrickSet().select_specific(id)
    brickset.update_checked('mini_col', state)

    # Info
    logger.info('Set {number} ({id}): changed minifigures collected status to {state}'.format(  # noqa: E501
        number=brickset.fields.set_num,
        id=brickset.fields.u_id,
        state=state,
    ))

    return jsonify({'state': state})


# Update the missing pieces of a minifig part
@set_page.route('/<id>/minifigures/<minifigure_id>/parts/<part_id>/missing', methods=['POST'])  # noqa: E501
@login_required
@exception_handler(__file__, json=True)
def missing_minifigure_part(
    *,
    id: str,
    minifigure_id: str,
    part_id: str
) -> Response:
    brickset = BrickSet().select_specific(id)
    minifigure = BrickMinifigure().select_specific(brickset, minifigure_id)
    part = BrickPart().select_specific(
        brickset,
        part_id,
        minifigure=minifigure,
    )

    missing = request.json.get('missing', '')  # type: ignore

    part.update_missing(missing)

    # Info
    logger.info('Set {number} ({id}): updated minifigure ({minifigure}) part ({part}) missing count to {missing}'.format(  # noqa: E501
        number=brickset.fields.set_num,
        id=brickset.fields.u_id,
        minifigure=minifigure.fields.fig_num,
        part=part.fields.id,
        missing=missing,
    ))

    return jsonify({'missing': missing})


# Update the missing pieces of a part
@set_page.route('/<id>/parts/<part_id>/missing', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def missing_part(*, id: str, part_id: str) -> Response:
    brickset = BrickSet().select_specific(id)
    part = BrickPart().select_specific(brickset, part_id)

    missing = request.json.get('missing', '')  # type: ignore

    part.update_missing(missing)

    # Info
    logger.info('Set {number} ({id}): updated part ({part}) missing count to {missing}'.format(  # noqa: E501
        number=brickset.fields.set_num,
        id=brickset.fields.u_id,
        part=part.fields.id,
        missing=missing,
    ))

    return jsonify({'missing': missing})
