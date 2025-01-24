from .instructions_list import BrickInstructionsList
from .retired_list import BrickRetiredList
from .set_checkbox_list import BrickSetCheckboxList
from .theme_list import BrickThemeList


# Reload everything related to a database after an operation
def reload() -> None:
    # Failsafe
    try:
        # Reload the instructions
        BrickInstructionsList(force=True)

        # Reload the checkboxes
        BrickSetCheckboxList(force=True)

        # Reload retired sets
        BrickRetiredList(force=True)

        # Reload themes
        BrickThemeList(force=True)
    except Exception:
        pass
