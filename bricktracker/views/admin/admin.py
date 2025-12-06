import logging
import os

from flask import Blueprint, request, render_template, current_app, jsonify
from flask_login import login_required

from ...configuration_list import BrickConfigurationList
from ...config_manager import ConfigManager
from ...config import CONFIG
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


def get_env_values():
    """Get current environment values, using defaults from config when not set"""
    from pathlib import Path

    env_values = {}
    config_defaults = {}
    env_explicit_values = {}  # Track which values are explicitly set
    env_locked_values = {}  # Track which values are set via Docker environment (locked)

    # Read .env file if it exists (check both locations)
    env_file = None
    if Path('data/.env').exists():
        env_file = Path('data/.env')
    elif Path('.env').exists():
        env_file = Path('.env')

    env_from_file = {}
    if env_file:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Strip quotes from value when reading
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    env_from_file[key] = value

    # Process each config item
    for config_item in CONFIG:
        env_name = f"BK_{config_item['n']}"

        # Store default value (with casting applied)
        default_value = config_item.get('d', '')
        if 'c' in config_item and default_value is not None:
            cast_type = config_item['c']
            if cast_type == bool and default_value == '':
                default_value = False  # Default for booleans is False only if no default specified
            elif cast_type == list and isinstance(default_value, str):
                default_value = [item.strip() for item in default_value.split(',') if item.strip()]
            # For int/other types, keep the original default value
        config_defaults[env_name] = default_value

        # Check if value is set via Docker environment and overrides .env file
        # A variable is "locked" if:
        # 1. It's set in os.environ (Docker environment), AND
        # 2. Either it's NOT in .env file, OR the value differs from .env file
        is_locked = False
        if env_name in os.environ:
            env_value = os.environ[env_name]
            file_value = env_from_file.get(env_name)
            # Locked if not in file, or values differ
            if file_value is None or env_value != file_value:
                is_locked = True
        env_locked_values[env_name] = is_locked

        # Check if value is explicitly set in .env file or environment
        is_explicitly_set = env_name in env_from_file or env_name in os.environ
        env_explicit_values[env_name] = is_explicitly_set

        # Get value from .env file, environment, or default
        value = env_from_file.get(env_name) or os.environ.get(env_name)
        if value is None:
            value = default_value
        else:
            # Apply casting if specified
            if 'c' in config_item and value is not None:
                cast_type = config_item['c']
                if cast_type == bool and isinstance(value, str):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif cast_type == int and value != '':
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        value = config_item.get('d', 0)
                elif cast_type == list and isinstance(value, str):
                    value = [item.strip() for item in value.split(',') if item.strip()]

        env_values[env_name] = value

    return env_values, config_defaults, env_explicit_values, env_locked_values


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

    # Get configurable default expanded sections
    default_expanded_sections = current_app.config.get('ADMIN_DEFAULT_EXPANDED_SECTIONS', [])

    # Helper function to check if section should be expanded
    def should_expand(section_name, url_param):
        # URL parameter takes priority over default config
        if url_param is not None:
            return url_param
        # Check if section is in default expanded list
        return section_name in default_expanded_sections

    # Apply configurable default expansion logic
    open_database = should_expand('database', request.args.get('open_database', None))
    open_image = should_expand('image', open_image)
    open_instructions = should_expand('instructions', open_instructions)
    open_logout = should_expand('authentication', open_logout)
    open_retired = should_expand('retired', open_retired)
    open_theme = should_expand('theme', open_theme)

    # Metadata sub-sections
    open_owner = should_expand('owner', open_owner)
    open_purchase_location = should_expand('purchase_location', open_purchase_location)
    open_status = should_expand('status', open_status)
    open_storage = should_expand('storage', open_storage)
    open_tag = should_expand('tag', open_tag)

    # Recalculate metadata section based on sub-sections or direct config
    open_metadata = (
        should_expand('metadata', open_metadata) or
        open_owner or
        open_purchase_location or
        open_status or
        open_storage or
        open_tag
    )

    env_values, config_defaults, env_explicit_values, env_locked_values = get_env_values()

    # Check .env file location and set warnings
    env_file_location = None
    env_file_warning = False
    env_file_missing = False

    if os.path.exists('data/.env'):
        env_file_location = 'data/.env'
        env_file_warning = False
        env_file_missing = False
    elif os.path.exists('.env'):
        env_file_location = '.env'
        env_file_warning = True  # Warn: changes won't persist without volume mount
        env_file_missing = False
    else:
        env_file_location = None
        env_file_warning = False
        env_file_missing = True  # Warn: no .env file found

    return render_template(
        'admin.html',
        configuration=BrickConfigurationList.list(),
        env_values=env_values,
        config_defaults=config_defaults,
        env_explicit_values=env_explicit_values,
        env_locked_values=env_locked_values,
        env_file_location=env_file_location,
        env_file_warning=env_file_warning,
        env_file_missing=env_file_missing,
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


# API Endpoints for Configuration Management

@admin_page.route('/api/config/update', methods=['POST'])
@login_required
@exception_handler(__file__)
def update_config() -> str:
    """Update live configuration variables"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400

        updates = data.get('updates', {})
        if not updates:
            return jsonify({
                'status': 'error',
                'message': 'No updates provided'
            }), 400

        # Use ConfigManager to update live configuration
        config_manager = ConfigManager()
        results = config_manager.update_config(updates)

        # Check if all updates were successful
        successful_updates = {k: v for k, v in results.items() if "successfully" in v}
        failed_updates = {k: v for k, v in results.items() if "successfully" not in v}

        logger.info(f"Configuration update: {len(successful_updates)} successful, {len(failed_updates)} failed")

        if failed_updates:
            logger.warning(f"Failed updates: {failed_updates}")

        return jsonify({
            'status': 'success' if not failed_updates else 'partial',
            'results': results,
            'successful_count': len(successful_updates),
            'failed_count': len(failed_updates)
        })

    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@admin_page.route('/api/config/update-static', methods=['POST'])
@login_required
@exception_handler(__file__)
def update_static_config() -> str:
    """Update static configuration variables (requires restart)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400

        updates = data.get('updates', {})
        if not updates:
            return jsonify({
                'status': 'error',
                'message': 'No updates provided'
            }), 400

        # Use ConfigManager to update .env file
        config_manager = ConfigManager()

        # Update each variable in the .env file
        updated_count = 0
        for var_name, value in updates.items():
            try:
                config_manager._update_env_file(var_name, value)
                updated_count += 1
                logger.info(f"Updated static config: {var_name}")
            except Exception as e:
                logger.error(f"Failed to update static config {var_name}: {e}")
                raise e

        logger.info(f"Updated {updated_count} static configuration variables")

        return jsonify({
            'status': 'success',
            'message': f'Successfully updated {updated_count} static configuration variables to .env file',
            'updated_count': updated_count
        })

    except Exception as e:
        logger.error(f"Error updating static configuration: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
