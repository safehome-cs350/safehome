"""User."""


class User:
    """User class."""

    def __init__(self, user_id: str, password1: str, password2: str):
        """Initialize user."""
        self.user_id = user_id
        self.password1 = password1
        self.password2 = password2


class UserDB:
    """User database class."""

    users = [User("homeowner1", "12345678", "abcdefgh")]

    @classmethod
    def find_user_by_id(cls, user_id: str) -> User | None:
        """Find a user by ID."""
        return next((u for u in cls.users if u.user_id == user_id), None)
