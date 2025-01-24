import logging
import os
from typing import Generator, TYPE_CHECKING

from flask import current_app

from .exceptions import NotFoundException
from .instructions import BrickInstructions
from .rebrickable_set_list import RebrickableSetList
if TYPE_CHECKING:
    from .rebrickable_set import RebrickableSet

logger = logging.getLogger(__name__)


# Lego sets instruction list
class BrickInstructionsList(object):
    all: dict[str, BrickInstructions]
    rejected_total: int
    sets: dict[str, list[BrickInstructions]]
    sets_total: int
    unknown_total: int

    def __init__(self, /, *, force=False):
        # Load instructions only if there is none already loaded
        all = getattr(self, 'all', None)

        if all is None or force:
            logger.info('Loading instructions file list')

            BrickInstructionsList.all = {}
            BrickInstructionsList.rejected_total = 0
            BrickInstructionsList.sets = {}
            BrickInstructionsList.sets_total = 0
            BrickInstructionsList.unknown_total = 0

            # Try to list the files in the instruction folder
            try:
                # Make a folder relative to static
                folder: str = os.path.join(
                    current_app.static_folder,  # type: ignore
                    current_app.config['INSTRUCTIONS_FOLDER'],
                )

                for file in os.scandir(folder):
                    instruction = BrickInstructions(file)

                    # Unconditionnally add to the list
                    BrickInstructionsList.all[instruction.filename] = instruction  # noqa: E501

                    if instruction.allowed:
                        if instruction.set:
                            # Instantiate the list if not existing yet
                            if instruction.set not in BrickInstructionsList.sets:  # noqa: E501
                                BrickInstructionsList.sets[instruction.set] = []  # noqa: E501

                            BrickInstructionsList.sets[instruction.set].append(instruction)  # noqa: E501
                            BrickInstructionsList.sets_total += 1
                        else:
                            BrickInstructionsList.unknown_total += 1
                    else:
                        BrickInstructionsList.rejected_total += 1

                # List of Rebrickable sets
                rebrickable_sets: dict[str, RebrickableSet] = {}
                for rebrickable_set in RebrickableSetList().all():
                    rebrickable_sets[rebrickable_set.fields.set] = rebrickable_set  # noqa: E501

                # Inject the brickset if it exists
                for instruction in self.all.values():
                    if (
                        instruction.allowed and
                        instruction.set is not None and
                        instruction.rebrickable is None and
                        instruction.set in rebrickable_sets
                    ):
                        instruction.rebrickable = rebrickable_sets[instruction.set]  # noqa: E501
            # Ignore errors
            except Exception:
                pass

    # Grab instructions for a set
    def get(self, set: str) -> list[BrickInstructions]:
        if set in self.sets:
            return self.sets[set]
        else:
            return []

    # Grab instructions for a file
    def get_file(self, name: str) -> BrickInstructions:
        if name not in self.all:
            raise NotFoundException('Instruction file {name} does not exist'.format(  # noqa: E501
                name=name
            ))

        return self.all[name]

    # List of all instruction files
    def list(self, /) -> Generator[BrickInstructions, None, None]:
        # Get the filenames and sort them
        filenames = list(self.all.keys())
        filenames.sort()

        # Return the files
        for filename in filenames:
            yield self.all[filename]
