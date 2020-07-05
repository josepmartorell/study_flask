from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

users = []


class User(UserMixin):
    def __init__(self, id, name, email, password, is_admin=False):
        self.id = id
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.is_admin = is_admin

    def set_password(self, password):
        """
        To avoid a security problem, instead of saving user passwords, we will save a password HASH using the
        werkzeug.security library.
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        The check_password method VERIFIES if the hash of the password parameter matches that of the user.
        """
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def get_user(email):
        for user in users:
            if user.email == email:
                return user
        return None
