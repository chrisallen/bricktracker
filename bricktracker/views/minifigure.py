from flask import Blueprint, render_template

from .exceptions import exception_handler
from ..minifigure import BrickMinifigure
from ..minifigure_list import BrickMinifigureList
from ..set_list import BrickSetList

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
@minifigure_page.route('/<number>/details')
@exception_handler(__file__)
def details(*, number: str) -> str:
    return render_template(
        'minifigure.html',
        item=BrickMinifigure().select_generic(number),
        using=BrickSetList().using_minifigure(number),
        missing=BrickSetList().missing_minifigure(number),
    )
