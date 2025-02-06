from flask import Blueprint, render_template

from .exceptions import exception_handler
from ..minifigure import BrickMinifigure
from ..minifigure_list import BrickMinifigureList
from ..set_list import BrickSetList, set_metadata_lists

minifigure_page = Blueprint('minifigure', __name__, url_prefix='/minifigures')


# Index
@minifigure_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'minifigures.html',
        table_collection=BrickMinifigureList().all(),
    )


# Minifigure details
@minifigure_page.route('/<figure>/details')
@exception_handler(__file__)
def details(*, figure: str) -> str:
    return render_template(
        'minifigure.html',
        item=BrickMinifigure().select_generic(figure),
        using=BrickSetList().using_minifigure(figure),
        missing=BrickSetList().missing_minifigure(figure),
        damaged=BrickSetList().damaged_minifigure(figure),
        **set_metadata_lists(as_class=True)
    )
