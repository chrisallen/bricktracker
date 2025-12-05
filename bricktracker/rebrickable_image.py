import os
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from flask import current_app, url_for
import requests
from shutil import copyfileobj

from .exceptions import DownloadException
if TYPE_CHECKING:
    from .rebrickable_minifigure import RebrickableMinifigure
    from .rebrickable_part import RebrickablePart
    from .rebrickable_set import RebrickableSet


# A set, part or minifigure image from Rebrickable
class RebrickableImage(object):
    set: 'RebrickableSet'
    minifigure: 'RebrickableMinifigure | None'
    part: 'RebrickablePart | None'

    extension: str | None

    def __init__(
        self,
        set: 'RebrickableSet',
        /,
        *,
        minifigure: 'RebrickableMinifigure | None' = None,
        part: 'RebrickablePart | None' = None,
    ):
        # Save all objects
        self.set = set
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

        # Check if the original image field is null - copy nil placeholder instead
        if self.part is not None and self.part.fields.image is None:
            return
        if self.minifigure is not None and self.minifigure.fields.image is None:
            return
        if self.set.fields.image is None:
            # Copy nil.png from parts folder to sets folder with set number as filename
            parts_folder = current_app.config['PARTS_FOLDER']
            if not os.path.isabs(parts_folder):
                parts_folder = os.path.join(current_app.root_path, parts_folder)
            nil_source = os.path.join(parts_folder, f"{RebrickableImage.nil_name()}.{self.extension}")

            if os.path.exists(nil_source):
                import shutil
                shutil.copy2(nil_source, path)
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
            return current_app.config['PARTS_FOLDER']

        if self.minifigure is not None:
            return current_app.config['MINIFIGURES_FOLDER']

        return current_app.config['SETS_FOLDER']

    # Return the id depending on the objects provided
    def id(self, /) -> str:
        if self.part is not None:
            if self.part.fields.image_id is None:
                return RebrickableImage.nil_name()
            else:
                return self.part.fields.image_id

        if self.minifigure is not None:
            if self.minifigure.fields.image is None:
                return RebrickableImage.nil_minifigure_name()
            else:
                return self.minifigure.fields.figure

        return self.set.fields.set

    # Return the path depending on the objects provided
    def path(self, /) -> str:
        folder = self.folder()
        # If folder is an absolute path (starts with /), use it directly
        # Otherwise, make it relative to app root (current_app.root_path)
        if folder.startswith('/'):
            base_path = folder
        else:
            base_path = os.path.join(current_app.root_path, folder)

        return os.path.join(
            base_path,
            '{id}.{ext}'.format(id=self.id(), ext=self.extension),
        )

    # Return the url depending on the objects provided
    def url(self, /) -> str:
        if self.part is not None:
            if self.part.fields.image is None:
                return current_app.config['REBRICKABLE_IMAGE_NIL']
            else:
                return self.part.fields.image

        if self.minifigure is not None:
            if self.minifigure.fields.image is None:
                return current_app.config['REBRICKABLE_IMAGE_NIL_MINIFIGURE']
            else:
                return self.minifigure.fields.image

        # Handle set images - use nil placeholder if image is null
        if self.set.fields.image is None:
            return current_app.config['REBRICKABLE_IMAGE_NIL']
        else:
            return self.set.fields.image

    # Return the name of the nil image file
    @staticmethod
    def nil_name() -> str:
        filename, _ = os.path.splitext(
            os.path.basename(
                urlparse(current_app.config['REBRICKABLE_IMAGE_NIL']).path
            )
        )

        return filename

    # Return the name of the nil minifigure image file
    @staticmethod
    def nil_minifigure_name() -> str:
        filename, _ = os.path.splitext(
            os.path.basename(
                urlparse(current_app.config['REBRICKABLE_IMAGE_NIL_MINIFIGURE']).path  # noqa: E501
            )
        )

        return filename

    # Return the static URL for an image given a name and folder
    @staticmethod
    def static_url(name: str, folder_name: str) -> str:
        folder: str = current_app.config[folder_name]

        # /!\ Everything is saved as .jpg, even if it came from a .png
        # not changing this behaviour.

        # Grab the extension
        # _, extension = os.path.splitext(self.part_img_url)
        extension = '.jpg'

        # Determine which route to use based on folder path
        # If folder contains 'data' (new structure), use data route
        # Otherwise use static route (legacy - relative paths like 'parts', 'sets')
        if 'data' in folder:
            # Extract the folder type from the folder_name config key
            # E.g., 'PARTS_FOLDER' -> 'parts', 'SETS_FOLDER' -> 'sets'
            folder_type = folder_name.replace('_FOLDER', '').lower()
            filename = '{name}{ext}'.format(name=name, ext=extension)
            return url_for('data.serve_data_file', folder=folder_type, filename=filename)
        else:
            # Legacy: folder is relative to static/ (e.g., 'parts' or 'static/parts')
            # Strip 'static/' prefix if present to avoid double /static/ in URL
            folder_clean = folder.removeprefix('static/')
            path = os.path.join(folder_clean, '{name}{ext}'.format(
                name=name,
                ext=extension,
            ))
            return url_for('static', filename=path)
