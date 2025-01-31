from .instructions_list import BrickInstructionsList
from .retired_list import BrickRetiredList
from .set_owner import BrickSetOwner
from .set_owner_list import BrickSetOwnerList
from .set_status import BrickSetStatus
from .set_status_list import BrickSetStatusList
from .theme_list import BrickThemeList


# Reload everything related to a database after an operation
def reload() -> None:
    # Failsafe
    try:
        # Reload the instructions
        BrickInstructionsList(force=True)

        # Reload the set owners
        BrickSetOwnerList(BrickSetOwner, force=True)

        # Reload the set statuses
        BrickSetStatusList(BrickSetStatus, force=True)

        # Reload retired sets
        BrickRetiredList(force=True)

        # Reload themes
        BrickThemeList(force=True)
    except Exception:
        pass
