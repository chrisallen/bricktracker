import logging

from flask import Blueprint, request, render_template
from flask_login import login_required

from ...configuration_list import BrickConfigurationList
from ..exceptions import exception_handler
from ...instructions_list import BrickInstructionsList
from ...rebrickable_image import RebrickableImage
from ...retired_list import BrickRetiredList
from ...set_owner import BrickSetOwner
from ...set_owner_list import BrickSetOwnerList
from ...set_purchase_location import BrickSetPurchaseLocation
from ...set_purchase_location_list import BrickSetPurchaseLocationList
from ...set_storage import BrickSetStorage
from ...set_storage_list import BrickSetStorageList
from ...set_status import BrickSetStatus
from ...set_status_list import BrickSetStatusList
from ...set_tag import BrickSetTag
from ...set_tag_list import BrickSetTagList
from ...sql_counter import BrickCounter
from ...sql import BrickSQL
from ...theme_list import BrickThemeList

logger = logging.getLogger(__name__)

admin_page = Blueprint('admin', __name__, url_prefix='/admin')


# Admin
@admin_page.route('/', methods=['GET'])
@login_required
@exception_handler(__file__)
def admin() -> str:
    database_counters: list[BrickCounter] = []
    database_exception: Exception | None = None
    database_upgrade_needed: bool = False
    database_version: int = -1
    instructions: BrickInstructionsList | None = None
    metadata_owners: list[BrickSetOwner] = []
    metadata_purchase_locations: list[BrickSetPurchaseLocation] = []
    metadata_statuses: list[BrickSetStatus] = []
    metadata_storages: list[BrickSetStorage] = []
    metadata_tags: list[BrickSetTag] = []
    nil_minifigure_name: str = ''
    nil_minifigure_url: str = ''
    nil_part_name: str = ''
    nil_part_url: str = ''

    # This view needs to be protected against SQL errors
    try:
        database = BrickSQL(failsafe=True)
        database_upgrade_needed = database.upgrade_needed()
        database_version = database.version
        database_counters = BrickSQL().count_records()

        instructions = BrickInstructionsList()

        metadata_owners = BrickSetOwnerList.list()
        metadata_purchase_locations = BrickSetPurchaseLocationList.list()
        metadata_statuses = BrickSetStatusList.list(all=True)
        metadata_storages = BrickSetStorageList.list()
        metadata_tags = BrickSetTagList.list()
    except Exception as e:
        database_exception = e

        # Warning
        logger.warning('A database exception occured while loading the admin page: {exception}'.format(  # noqa: E501
            exception=str(e),
        ))

    nil_minifigure_name = RebrickableImage.nil_minifigure_name()
    nil_minifigure_url = RebrickableImage.static_url(
        nil_minifigure_name,
        'MINIFIGURES_FOLDER'
    )

    nil_part_name = RebrickableImage.nil_name()
    nil_part_url = RebrickableImage.static_url(
        nil_part_name,
        'PARTS_FOLDER'
    )

    open_image = request.args.get('open_image', None)
    open_instructions = request.args.get('open_instructions', None)
    open_logout = request.args.get('open_logout', None)
    open_metadata = request.args.get('open_metadata', None)
    open_owner = request.args.get('open_owner', None)
    open_purchase_location = request.args.get('open_purchase_location', None)
    open_retired = request.args.get('open_retired', None)
    open_status = request.args.get('open_status', None)
    open_storage = request.args.get('open_storage', None)
    open_tag = request.args.get('open_tag', None)
    open_theme = request.args.get('open_theme', None)

    open_metadata = (
        open_metadata or
        open_owner or
        open_purchase_location or
        open_status or
        open_storage or
        open_tag
    )

    open_database = (
        open_image is None and
        open_instructions is None and
        open_logout is None and
        not open_metadata and
        open_retired is None and
        open_theme is None
    )

    return render_template(
        'admin.html',
        configuration=BrickConfigurationList.list(),
        database_counters=database_counters,
        database_error=request.args.get('database_error'),
        database_exception=database_exception,
        database_upgrade_needed=database_upgrade_needed,
        database_version=database_version,
        instructions=instructions,
        metadata_owners=metadata_owners,
        metadata_purchase_locations=metadata_purchase_locations,
        metadata_statuses=metadata_statuses,
        metadata_storages=metadata_storages,
        metadata_tags=metadata_tags,
        nil_minifigure_name=nil_minifigure_name,
        nil_minifigure_url=nil_minifigure_url,
        nil_part_name=nil_part_name,
        nil_part_url=nil_part_url,
        open_database=open_database,
        open_image=open_image,
        open_instructions=open_instructions,
        open_logout=open_logout,
        open_metadata=open_metadata,
        open_owner=open_owner,
        open_purchase_location=open_purchase_location,
        open_retired=open_retired,
        open_status=open_status,
        open_storage=open_storage,
        open_tag=open_tag,
        open_theme=open_theme,
        owner_error=request.args.get('owner_error'),
        purchase_location_error=request.args.get('purchase_location_error'),
        retired=BrickRetiredList(),
        status_error=request.args.get('status_error'),
        storage_error=request.args.get('storage_error'),
        tag_error=request.args.get('tag_error'),
        theme=BrickThemeList(),
    )
