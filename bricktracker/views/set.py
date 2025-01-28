import logging

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
from ..minifigure import BrickMinifigure
from ..part import BrickPart
from ..set import BrickSet
from ..set_checkbox_list import BrickSetCheckboxList
from ..set_list import BrickSetList
from ..socket import MESSAGES

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
    logger.info('Set {set} ({id}): status "{status}" changed to "{state}"'.format(  # noqa: E501
        set=brickset.fields.set,
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
    logger.info('Set {set} ({id}): deleted'.format(
        set=brickset.fields.set,
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


# Update the missing pieces of a part
@set_page.route('/<id>/parts/<part>/<int:color>/<int:spare>/missing', defaults={'figure': None}, methods=['POST'])  # noqa: E501
@set_page.route('/<id>/minifigures/<figure>/parts/<part>/<int:color>/<int:spare>/missing', methods=['POST'])  # noqa: E501
@login_required
@exception_handler(__file__, json=True)
def missing_part(
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

    missing = request.json.get('missing', '')  # type: ignore

    brickpart.update_missing(missing)

    # Info
    logger.info('Set {set} ({id}): updated part ({part} color: {color}, spare: {spare}, minifigure: {figure}) missing count to {missing}'.format(  # noqa: E501
        set=brickset.fields.set,
        id=brickset.fields.id,
        figure=figure,
        part=brickpart.fields.part,
        color=brickpart.fields.color,
        spare=brickpart.fields.spare,
        missing=brickpart.fields.missing,
    ))

    return jsonify({'missing': missing})


# Refresh a set
@set_page.route('/<id>/refresh', methods=['GET'])
@exception_handler(__file__)
def refresh(*, id: str) -> str:
    return render_template(
        'refresh.html',
        item=BrickSet().select_specific(id),
        path=current_app.config['SOCKET_PATH'],
        namespace=current_app.config['SOCKET_NAMESPACE'],
        messages=MESSAGES
    )
