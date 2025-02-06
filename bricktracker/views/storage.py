from flask import Blueprint, render_template

from .exceptions import exception_handler
from ..set_list import BrickSetList, set_metadata_lists
from ..set_storage import BrickSetStorage
from ..set_storage_list import BrickSetStorageList

storage_page = Blueprint('storage', __name__, url_prefix='/storages')


# Index
@storage_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'storages.html',
        table_collection=BrickSetStorageList.all(),
    )


# Storage details
@storage_page.route('/<id>/details')
@exception_handler(__file__)
def details(*, id: str) -> str:
    storage = BrickSetStorage().select_specific(id)

    return render_template(
        'storage.html',
        item=storage,
        sets=BrickSetList().using_storage(storage),
        **set_metadata_lists(as_class=True)
    )
