from flask import Blueprint, render_template, request

from .exceptions import exception_handler
from ..minifigure_list import BrickMinifigureList
from ..part import BrickPart
from ..part_list import BrickPartList
from ..set_list import BrickSetList, set_metadata_lists
from ..set_owner_list import BrickSetOwnerList
from ..sql import BrickSQL

part_page = Blueprint('part', __name__, url_prefix='/parts')


# Index
@part_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    
    # Get filter parameters from request
    owner_id = request.args.get('owner', 'all')
    color_id = request.args.get('color', 'all')

    # Get parts with filters applied
    parts = BrickPartList().all_filtered(owner_id, color_id)

    # Get list of owners for filter dropdown
    owners = BrickSetOwnerList.list()

    # Get list of colors for filter dropdown
    # Prepare context for color query (filter by owner if selected)
    color_context = {}
    if owner_id != 'all' and owner_id:
        color_context['owner_id'] = owner_id

    colors = BrickSQL().fetchall('part/colors/list', **color_context)

    return render_template(
        'parts.html',
        table_collection=parts,
        owners=owners,
        selected_owner=owner_id,
        colors=colors,
        selected_color=color_id,
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
