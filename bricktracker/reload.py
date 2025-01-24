from .instructions_list import BrickInstructionsList
from .retired_list import BrickRetiredList
from .theme_list import BrickThemeList


# Reload everything related to a database after an operation
def reload() -> None:
    # Failsafe
    try:
        # Reload the instructions
        BrickInstructionsList(force=True)

        # Reload retired sets
        BrickRetiredList(force=True)

        # Reload themes
        BrickThemeList(force=True)
    except Exception:
        pass
