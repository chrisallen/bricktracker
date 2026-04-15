from flask import Blueprint, render_template

from .exceptions import exception_handler
from ..set_list import BrickSetList, set_metadata_lists
from ..set_purchase_location import BrickSetPurchaseLocation
from ..set_purchase_location_list import BrickSetPurchaseLocationList
from ..individual_minifigure_list import IndividualMinifigureList
from ..individual_part_list import IndividualPartList
from ..individual_part_lot_list import IndividualPartLotList

purchase_location_page = Blueprint('purchase_location', __name__, url_prefix='/purchase-locations')


# Index
@purchase_location_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'purchase_locations.html',
        table_collection=BrickSetPurchaseLocationList.all(),
    )


# Purchase location details
@purchase_location_page.route('/<id>/details')
@exception_handler(__file__)
def details(*, id: str) -> str:
    purchase_location = BrickSetPurchaseLocation().select_specific(id)

    return render_template(
        'purchase_location.html',
        item=purchase_location,
        sets=BrickSetList().using_purchase_location(purchase_location),
        individual_minifigures=IndividualMinifigureList().using_purchase_location(purchase_location),
        individual_parts=IndividualPartList().using_purchase_location(purchase_location),
        individual_part_lots=IndividualPartLotList().using_purchase_location(purchase_location),
        **set_metadata_lists(as_class=True)
    )
