from flask import Blueprint, render_template

from .exceptions import exception_handler
from ..minifigure_list import BrickMinifigureList
from ..part import BrickPart
from ..part_list import BrickPartList
from ..set_list import BrickSetList, set_metadata_lists

part_page = Blueprint('part', __name__, url_prefix='/parts')


# Index
@part_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'parts.html',
        table_collection=BrickPartList().all()
    )


# Problem
@part_page.route('/problem', methods=['GET'])
@exception_handler(__file__)
def problem() -> str:
    return render_template(
        'problem.html',
        table_collection=BrickPartList().problem()
    )


# Part details
@part_page.route('/<part>/<int:color>/details', methods=['GET'])  # noqa: E501
@exception_handler(__file__)
def details(*, part: str, color: int) -> str:
    brickpart = BrickPart().select_generic(part, color)

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
        **set_metadata_lists(as_class=True)
    )
