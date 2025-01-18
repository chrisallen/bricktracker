import logging

from flask import (
    Blueprint,
    current_app,
    g,
    redirect,
    render_template,
    request,
    url_for
)
from flask_login import (
    AnonymousUserMixin,
    current_user,
    login_user,
    logout_user
)
from werkzeug.wrappers.response import Response

from .exceptions import exception_handler
from ..login import LoginManager

logger = logging.getLogger(__name__)

login_page = Blueprint('login', __name__)


# Index
@login_page.route('/login', methods=['GET'])
@exception_handler(__file__)
def login() -> str | Response:
    # Do not log if logged in
    if g.login.is_authenticated():
        return redirect(url_for('index.index'))

    return render_template(
        'login.html',
        next=request.args.get('next'),
        wrong_password=request.args.get('wrong_password'),
    )


# Authenticate the user
@login_page.route('/login', methods=['POST'])
@exception_handler(__file__)
def do_login() -> Response:
    # Grab our unique user
    user: LoginManager.User = current_app.login_manager.user_callback()  # type: ignore # noqa: E501

    # Security: Does not check if the next url is compromised
    next = request.args.get('next')

    # Grab the password
    password: str = request.form.get('password', '')

    if password == '' or user.password != password:
        return redirect(url_for('login.login', wrong_password=True, next=next))

    # Set the user as logged in
    login_user(user)

    # Info
    logger.info('{user}: logged in'.format(
        user=user.id,
    ))

    # Disconnect all sockets
    current_app.config['_SOCKET'].emit('DISCONNECT', all=True)

    # Redirect the user
    return redirect(next or url_for('index.index'))


# Logout
@login_page.route('/logout', methods=['GET'])
@exception_handler(__file__)
def logout() -> Response:
    if not isinstance(current_user, AnonymousUserMixin):
        id = current_user.id

        logout_user()

        # Info
        logger.info('{user}: logged out'.format(
            user=id,
        ))

    # Disconnect all sockets
    current_app.config['_SOCKET'].emit('DISCONNECT', all=True)

    return redirect(url_for('index.index'))
