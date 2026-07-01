"""画面や保存方法に依存しない認証ルールを提供します。"""

import re

from .interfaces import PasswordHasher, UserRepository
from .models import RegistrationResult, User


class AuthenticationService:
    """利用者登録とログイン判定を担当するサービスです。"""

    # 利用できるユーザー名の形式です。
    _USERNAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")

    def __init__(self, repository: UserRepository, hasher: PasswordHasher) -> None:
        # 利用者情報の取得と保存を担当する部品です。
        self._repository = repository
        # パスワードの安全な変換と照合を担当する部品です。
        self._hasher = hasher

    def normalize_username(self, username: str) -> str:
        """前後の空白と大文字小文字を統一します。"""
        return username.strip().casefold()

    def has_users(self) -> bool:
        """利用者が登録済みか返します。"""
        return self._repository.has_users()

    def register_initial_user(self, username: str, password: str) -> RegistrationResult:
        """入力を検証し、最初の利用者だけを登録します。"""
        normalized_username = self.normalize_username(username)
        if not self._USERNAME_PATTERN.fullmatch(normalized_username):
            return RegistrationResult(False, "ユーザー名は3〜64文字の半角英数字、ピリオド、ハイフン、下線で入力してください。")
        if not self._is_valid_password(password):
            return RegistrationResult(False, "パスワードは12〜128文字で、英字と数字をそれぞれ含めてください。")

        # 平文パスワードは保存せず、直ちにハッシュ化します。
        user = User(normalized_username, self._hasher.hash(password))
        if not self._repository.add_initial_user(user):
            return RegistrationResult(False, "初回アカウントは既に登録されています。")
        return RegistrationResult(True, "アカウントを作成しました。")

    def authenticate(self, username: str, password: str) -> bool:
        """利用者名とパスワードが正しい場合だけ認証します。"""
        if len(username) > 64 or len(password) > 128:
            return False
        user = self._repository.find_by_username(self.normalize_username(username))
        if user is None:
            return False
        return self._hasher.verify(password, user.password_hash)

    @staticmethod
    def _is_valid_password(password: str) -> bool:
        """長さと文字種を確認し、最低限のパスワード強度を保証します。"""
        return 12 <= len(password) <= 128 and any(c.isalpha() for c in password) and any(c.isdigit() for c in password)
