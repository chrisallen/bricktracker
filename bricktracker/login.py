from flask import current_app, Flask
from flask_login import current_user, login_manager, UserMixin


# Login manager wrapper
class LoginManager(object):
    # Login user
    class User(UserMixin):
        def __init__(self, name: str, password: str, /):
            self.id = name
            self.password = password

    def __init__(self, app: Flask, /):
        # Setup basic authentication
        app.secret_key = app.config['AUTHENTICATION_KEY']

        manager = login_manager.LoginManager()
        manager.login_view = 'login.login'  # type: ignore
        manager.init_app(app)

        # User loader with only one user
        @manager.user_loader
        def user_loader(*arg) -> LoginManager.User:
            return self.User(
                'admin',
                app.config['AUTHENTICATION_PASSWORD']
            )

        # If the password is unset, globally disable
        app.config['LOGIN_DISABLED'] = app.config['AUTHENTICATION_PASSWORD'] == ''  # noqa: E501

    # Tells whether the user is authenticated, meaning:
    # - Authentication disabled
    # - or User is authenticated
    @staticmethod
    def is_authenticated() -> bool:
        return (
            current_app.config['LOGIN_DISABLED'] or
            current_user.is_authenticated
        )

    # Tells whether authentication is enabled
    @staticmethod
    def is_enabled() -> bool:
        return not current_app.config['LOGIN_DISABLED']

    # Tells whether we need the user authenticated, meaning:
    # - Authentication enabled
    # - and User not authenticated
    @staticmethod
    def is_not_authenticated() -> bool:
        return (
            not current_app.config['LOGIN_DISABLED'] and
            not current_user.is_authenticated
        )
