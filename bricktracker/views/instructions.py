from flask import (
    current_app,
    Blueprint,
    redirect,
    render_template,
    request,
    url_for
)
from flask_login import login_required
from werkzeug.wrappers.response import Response
from werkzeug.utils import secure_filename

from .exceptions import exception_handler
from ..instructions import BrickInstructions
from ..instructions_list import BrickInstructionsList
from ..parser import parse_set
from ..peeron_instructions import PeeronInstructions
from ..socket import MESSAGES
from .upload import upload_helper

instructions_page = Blueprint(
    'instructions',
    __name__,
    url_prefix='/instructions'
)


def _render_peeron_select_page(set: str) -> str:
    """Helper function to render the Peeron page selection interface with cached thumbnails."""
    peeron = PeeronInstructions(set)
    peeron_pages = peeron.find_pages()  # This will use the cached thumbnails
    current_app.logger.debug(f"[peeron_loaded] Found {len(peeron_pages)} pages for {set}")
    return render_template(
        'peeron_select.html',
        download=True,
        pages=peeron_pages,
        set=set,
        path=current_app.config['SOCKET_PATH'],
        namespace=current_app.config['SOCKET_NAMESPACE'],
        messages=MESSAGES
    )


# Index
@instructions_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'instructions.html',
        table_collection=BrickInstructionsList().list(),
    )


# Delete an instructions file
@instructions_page.route('/<name>/delete/', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, name: str) -> str:
    return render_template(
        'instructions.html',
        item=BrickInstructionsList().get_file(name),
        delete=True,
        error=request.args.get('error')
    )


# Actually delete an instructions file
@instructions_page.route('/<name>/delete/', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='instructions.delete')
def do_delete(*, name: str) -> Response:
    instruction = BrickInstructionsList().get_file(name)

    # Delete the instructions file
    instruction.delete()

    # Reload the instructions
    BrickInstructionsList(force=True)

    return redirect(url_for('instructions.list'))


# Rename an instructions file
@instructions_page.route('/<name>/rename/', methods=['GET'])
@login_required
@exception_handler(__file__)
def rename(*, name: str) -> str:
    return render_template(
        'instructions.html',
        item=BrickInstructionsList().get_file(name),
        rename=True,
        error=request.args.get('error')
    )


# Actually rename an instructions file
@instructions_page.route('/<name>/rename/', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='instructions.rename')
def do_rename(*, name: str) -> Response:
    instruction = BrickInstructionsList().get_file(name)

    # Grab the new filename
    filename = secure_filename(request.form.get('filename', ''))

    if filename != '':
        # Delete the instructions file
        instruction.rename(filename)

        # Reload the instructions
        BrickInstructionsList(force=True)

    return redirect(url_for('instructions.list'))


# Upload an instructions file
@instructions_page.route('/upload/', methods=['GET'])
@login_required
@exception_handler(__file__)
def upload() -> str:
    return render_template(
        'instructions.html',
        upload=True,
        error=request.args.get('error')
    )


# Actually upload an instructions file
@instructions_page.route('/upload', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='instructions.upload')
def do_upload() -> Response:
    file = upload_helper(
        'file',
        'instructions.upload',
        extensions=current_app.config['INSTRUCTIONS_ALLOWED_EXTENSIONS'],
    )

    if isinstance(file, Response):
        return file

    BrickInstructions(file.filename).upload(file)  # type: ignore

    # Reload the instructions
    BrickInstructionsList(force=True)

    return redirect(url_for('instructions.list'))


# Download instructions from LEGO.com
@instructions_page.route('/download/', methods=['GET'])
@login_required
@exception_handler(__file__)
def download() -> str:
    # Grab the set number
    try:
        set = parse_set(request.args.get('set', ''))
    except Exception:
        set = ''

    # Check if this is a redirect after Peeron pages were loaded
    if request.args.get('peeron_loaded'):
        return _render_peeron_select_page(set)

    return render_template(
        'instructions.html',
        download=True,
        error=request.args.get('error'),
        set=set
    )


# Show search results
@instructions_page.route('/download', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='instructions.download')
def do_download() -> str:
    # Grab the set number
    try:
        set = parse_set(request.form.get('download-set', ''))
    except Exception:
        set = ''

    # Check if this is a redirect after Peeron pages were loaded
    if request.args.get('peeron_loaded'):
        return _render_peeron_select_page(set)

    # Try LEGO.com first
    try:
        from .instructions import BrickInstructions
        rebrickable_instructions = BrickInstructions.find_instructions(set)
        # Standard LEGO.com instructions found
        return render_template(
            'instructions.html',
            download=True,
            instructions=rebrickable_instructions,
            set=set,
            path=current_app.config['SOCKET_PATH'],
            namespace=current_app.config['SOCKET_NAMESPACE'],
            messages=MESSAGES
        )
    except Exception:
        # LEGO.com failed, check if Peeron has instructions (without caching thumbnails yet)
        try:
            peeron = PeeronInstructions(set)
            # Just check if pages exist, don't cache thumbnails yet
            if peeron.exists():
                # Peeron has instructions - show loading interface
                return render_template(
                    'peeron_select.html',
                    download=True,
                    loading_peeron=True,  # Flag to show loading state
                    set=set,
                    path=current_app.config['SOCKET_PATH'],
                    namespace=current_app.config['SOCKET_NAMESPACE'],
                    messages=MESSAGES
                )
            else:
                raise Exception("Not found on Peeron either")
        except Exception:
            return render_template(
                'instructions.html',
                download=True,
                instructions=[],
                set=set,
                error='No instructions found on LEGO.com or Peeron',
                path=current_app.config['SOCKET_PATH'],
                namespace=current_app.config['SOCKET_NAMESPACE'],
                messages=MESSAGES
            )
