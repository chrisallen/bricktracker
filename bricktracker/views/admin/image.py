from flask import Blueprint, redirect, url_for
from flask_login import login_required
from werkzeug.wrappers.response import Response

from ..exceptions import exception_handler
from ...minifigure import BrickMinifigure
from ...part import BrickPart
from ...rebrickable_image import RebrickableImage
from ...set import BrickSet

admin_image_page = Blueprint(
    'admin_image',
    __name__,
    url_prefix='/admin/image'
)


# Update the default images
@admin_image_page.route('/update', methods=['GET'])
@login_required
@exception_handler(__file__)
def update() -> Response:
    # Abusing the object to create a 'nil' minifigure
    RebrickableImage(
        BrickSet(),
        minifigure=BrickMinifigure(record={
            'set_img_url': None,
        })
    ).download()

    # Abusing the object to create a 'nil' part
    RebrickableImage(
        BrickSet(),
        part=BrickPart(record={
            'part_img_url': None,
            'part_img_url_id': None
        })
    ).download()

    return redirect(url_for('admin.admin', open_image=True))
