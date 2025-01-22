import logging
import os
from typing import Generator

from flask import current_app

from .exceptions import NotFoundException
from .instructions import BrickInstructions

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
                        if instruction.number:
                            # Instantiate the list if not existing yet
                            if instruction.number not in BrickInstructionsList.sets:  # noqa: E501
                                BrickInstructionsList.sets[instruction.number] = []  # noqa: E501

                            BrickInstructionsList.sets[instruction.number].append(instruction)  # noqa: E501
                            BrickInstructionsList.sets_total += 1
                        else:
                            BrickInstructionsList.unknown_total += 1
                    else:
                        BrickInstructionsList.rejected_total += 1

                # Associate bricksets
                # Not ideal, to avoid a circular import
                from .set import BrickSet
                from .set_list import BrickSetList

                # Grab the generic list of sets
                bricksets: dict[str, BrickSet] = {}
                for brickset in BrickSetList().generic().records:
                    bricksets[brickset.fields.set_num] = brickset

                # Inject the brickset if it exists
                for instruction in self.all.values():
                    if (
                        instruction.allowed and
                        instruction.number is not None and
                        instruction.brickset is None and
                        instruction.number in bricksets
                    ):
                        instruction.brickset = bricksets[instruction.number]

            # Ignore errors
            except Exception:
                pass

    # Grab instructions for a set
    def get(self, number: str) -> list[BrickInstructions]:
        if number in self.sets:
            return self.sets[number]
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
