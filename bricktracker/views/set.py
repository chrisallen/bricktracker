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
from ..set_checkbox_list import BrickSetCheckboxList
from ..set_list import BrickSetList

logger = logging.getLogger(__name__)

set_page = Blueprint('set', __name__, url_prefix='/sets')


# List of all sets
@set_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'sets.html',
        collection=BrickSetList().all(),
        brickset_checkboxes=BrickSetCheckboxList().list(),
    )


# Change the status of a checkbox
@set_page.route('/<id>/status/<checkbox_id>', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_status(*, id: str, checkbox_id: str) -> Response:
    value: bool = request.json.get('value', False)  # type: ignore

    brickset = BrickSet().select_light(id)
    checkbox = BrickSetCheckboxList().get(checkbox_id)

    brickset.update_status(checkbox, value)

    # Info
    logger.info('Set {number} ({id}): status "{status}" changed to "{state}"'.format(  # noqa: E501
        number=brickset.fields.set,
        id=brickset.fields.id,
        status=checkbox.fields.name,
        state=value,
    ))

    return jsonify({'value': value})


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
    brickset = BrickSet().select_light(id)
    brickset.delete()

    # Info
    logger.info('Set {number} ({id}): deleted'.format(
        number=brickset.fields.set,
        id=brickset.fields.id,
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
        brickset_checkboxes=BrickSetCheckboxList().list(all=True),
    )


# Update the missing pieces of a minifig part
@set_page.route('/<id>/minifigures/<figure>/parts/<part>/missing', methods=['POST'])  # noqa: E501
@login_required
@exception_handler(__file__, json=True)
def missing_minifigure_part(*, id: str, figure: str, part: str) -> Response:
    brickset = BrickSet().select_specific(id)
    brickminifigure = BrickMinifigure().select_specific(brickset, figure)
    brickpart = BrickPart().select_specific(
        brickset,
        part,
        minifigure=brickminifigure,
    )

    missing = request.json.get('missing', '')  # type: ignore

    brickpart.update_missing(missing)

    # Info
    logger.info('Set {number} ({id}): updated minifigure ({figure}) part ({part}) missing count to {missing}'.format(  # noqa: E501
        number=brickset.fields.set,
        id=brickset.fields.id,
        figure=brickminifigure.fields.fig_num,
        part=brickpart.fields.id,
        missing=missing,
    ))

    return jsonify({'missing': missing})


# Update the missing pieces of a part
@set_page.route('/<id>/parts/<part>/missing', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def missing_part(*, id: str, part: str) -> Response:
    brickset = BrickSet().select_specific(id)
    brickpart = BrickPart().select_specific(brickset, part)

    missing = request.json.get('missing', '')  # type: ignore

    brickpart.update_missing(missing)

    # Info
    logger.info('Set {number} ({id}): updated part ({part}) missing count to {missing}'.format(  # noqa: E501
        number=brickset.fields.set,
        id=brickset.fields.id,
        part=brickpart.fields.id,
        missing=missing,
    ))

    return jsonify({'missing': missing})
