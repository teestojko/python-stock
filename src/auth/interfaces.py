"""認証機能の交換可能な部品が満たす約束を定義します。"""

from typing import Protocol
from .models import User


class UserRepository(Protocol):
    """利用者情報の保存先が実装するインターフェイスです。"""

    def has_users(self) -> bool: ...
    def find_by_username(self, username: str) -> User | None: ...
    def add_initial_user(self, user: User) -> bool: ...


class PasswordHasher(Protocol):
    """パスワード処理が実装するインターフェイスです。"""

    def hash(self, password: str) -> str: ...
    def verify(self, password: str, encoded_password: str) -> bool: ...
