from flask import Blueprint, render_template

from .exceptions import exception_handler
from ..minifigure_list import BrickMinifigureList
from ..part import BrickPart
from ..part_list import BrickPartList
from ..set_list import BrickSetList

part_page = Blueprint('part', __name__, url_prefix='/parts')


# Index
@part_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'parts.html',
        table_collection=BrickPartList().all()
    )


# Missing
@part_page.route('/missing', methods=['GET'])
@exception_handler(__file__)
def missing() -> str:
    return render_template(
        'missing.html',
        table_collection=BrickPartList().missing()
    )


# Part details
@part_page.route('/<part>/<int:color>/details', methods=['GET'])  # noqa: E501
@exception_handler(__file__)
def details(*, part: str, color: int) -> str:
    return render_template(
        'part.html',
        item=BrickPart().select_generic(part, color),
        sets_using=BrickSetList().using_part(
            part,
            color
        ),
        sets_missing=BrickSetList().missing_part(
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
    )
