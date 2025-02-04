from .instructions_list import BrickInstructionsList
from .retired_list import BrickRetiredList
from .set_owner_list import BrickSetOwnerList
from .set_purchase_location_list import BrickSetPurchaseLocationList
from .set_status_list import BrickSetStatusList
from .set_storage_list import BrickSetStorageList
from .set_tag_list import BrickSetTagList
from .theme_list import BrickThemeList
from .wish_owner_list import BrickWishOwnerList


# Reload everything related to a database after an operation
def reload() -> None:
    # Failsafe
    try:
        # Reload the instructions
        BrickInstructionsList(force=True)

        # Reload the set owners
        BrickSetOwnerList.new(force=True)

        # Reload the set purchase locations
        BrickSetPurchaseLocationList.new(force=True)

        # Reload the set statuses
        BrickSetStatusList.new(force=True)

        # Reload the set storages
        BrickSetStorageList.new(force=True)

        # Reload the set tags
        BrickSetTagList.new(force=True)

        # Reload retired sets
        BrickRetiredList(force=True)

        # Reload themes
        BrickThemeList(force=True)

        # Reload the wish owners
        BrickWishOwnerList.new(force=True)
    except Exception:
        pass
