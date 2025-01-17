import os
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from flask import current_app
import requests
from shutil import copyfileobj

from .exceptions import DownloadException
if TYPE_CHECKING:
    from .minifigure import BrickMinifigure
    from .part import BrickPart
    from .set import BrickSet


# A set, part or minifigure image from Rebrickable
class RebrickableImage(object):
    brickset: 'BrickSet'
    minifigure: 'BrickMinifigure | None'
    part: 'BrickPart | None'

    extension: str | None

    def __init__(
        self,
        brickset: 'BrickSet',
        /,
        minifigure: 'BrickMinifigure | None' = None,
        part: 'BrickPart | None' = None,
    ):
        # Save all objects
        self.brickset = brickset
        self.minifigure = minifigure
        self.part = part

        # Currently everything is saved as 'jpg'
        self.extension = 'jpg'

        # Guess the extension
        # url = self.url()
        # if url is not None:
        #     _, extension = os.path.splitext(url)
        #     # TODO: Add allowed extensions
        #     if extension != '':
        #         self.extension = extension

    # Import the image from Rebrickable
    def download(self, /) -> None:
        path = self.path()

        # Avoid doing anything if the file exists
        if os.path.exists(path):
            return

        url = self.url()
        if url is None:
            return

        # Grab the image
        response = requests.get(url, stream=True)
        if response.ok:
            with open(path, 'wb') as f:
                copyfileobj(response.raw, f)
        else:
            raise DownloadException('could not get image {id} at {url}'.format(
                id=self.id(),
                url=url,
            ))

    # Return the folder depending on the objects provided
    def folder(self, /) -> str:
        if self.part is not None:
            return current_app.config['PARTS_FOLDER'].value

        if self.minifigure is not None:
            return current_app.config['MINIFIGURES_FOLDER'].value

        return current_app.config['SETS_FOLDER'].value

    # Return the id depending on the objects provided
    def id(self, /) -> str:
        if self.part is not None:
            if self.part.fields.part_img_url_id is None:
                return RebrickableImage.nil_name()
            else:
                return self.part.fields.part_img_url_id

        if self.minifigure is not None:
            if self.minifigure.fields.set_img_url is None:
                return RebrickableImage.nil_minifigure_name()
            else:
                return self.minifigure.fields.fig_num

        return self.brickset.fields.set_num

    # Return the path depending on the objects provided
    def path(self, /) -> str:
        return os.path.join(
            current_app.static_folder,  # type: ignore
            self.folder(),
            '{id}.{ext}'.format(id=self.id(), ext=self.extension),
        )

    # Return the url depending on the objects provided
    def url(self, /) -> str:
        if self.part is not None:
            if self.part.fields.part_img_url is None:
                return current_app.config['REBRICKABLE_IMAGE_NIL'].value
            else:
                return self.part.fields.part_img_url

        if self.minifigure is not None:
            if self.minifigure.fields.set_img_url is None:
                return current_app.config['REBRICKABLE_IMAGE_NIL_MINIFIGURE'].value  # noqa: E501
            else:
                return self.minifigure.fields.set_img_url

        return self.brickset.fields.set_img_url

    # Return the name of the nil image file
    @staticmethod
    def nil_name() -> str:
        filename, _ = os.path.splitext(
            os.path.basename(
                urlparse(current_app.config['REBRICKABLE_IMAGE_NIL'].value).path  # noqa: E501
            )
        )

        return filename

    # Return the name of the nil minifigure image file
    @staticmethod
    def nil_minifigure_name() -> str:
        filename, _ = os.path.splitext(
            os.path.basename(
                urlparse(current_app.config['REBRICKABLE_IMAGE_NIL_MINIFIGURE'].value).path  # noqa: E501
            )
        )

        return filename
