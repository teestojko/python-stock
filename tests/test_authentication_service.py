"""認証サービスの主要な動作を確認します。"""

from src.auth.models import User
from src.auth.service import AuthenticationService


class InMemoryUserRepository:
    """外部ファイルを使わず認証サービスを試験する保存先です。"""

    def __init__(self) -> None:
        # テスト中だけ保持する利用者です。
        self.user: User | None = None

    def has_users(self) -> bool:
        """テスト用利用者の有無を返します。"""
        return self.user is not None

    def find_by_username(self, username: str) -> User | None:
        """利用者名が一致したテスト用利用者を返します。"""
        return self.user if self.user and self.user.username == username else None

    def add_initial_user(self, user: User) -> bool:
        """最初の1件だけテスト用利用者を保存します。"""
        if self.user is not None:
            return False
        self.user = user
        return True


class SimplePasswordHasher:
    """サービスのルールだけを検証するテスト用部品です。"""

    def hash(self, password: str) -> str:
        """テスト専用の識別可能な値を返します。"""
        return f"test:{password}"

    def verify(self, password: str, encoded_password: str) -> bool:
        """テスト専用の保存値と入力値を比較します。"""
        return encoded_password == self.hash(password)


def create_service() -> AuthenticationService:
    """各テストで使用する認証サービスを作成します。"""
    return AuthenticationService(InMemoryUserRepository(), SimplePasswordHasher())


def test_initial_user_can_register_and_login() -> None:
    """初回登録後に正しい情報でログインできることを確認します。"""
    service = create_service()
    result = service.register_initial_user(" Example.User ", "securePassword123")
    assert result.success is True
    assert service.authenticate("example.user", "securePassword123") is True


def test_wrong_password_is_rejected() -> None:
    """誤ったパスワードではログインできないことを確認します。"""
    service = create_service()
    service.register_initial_user("example-user", "securePassword123")
    assert service.authenticate("example-user", "wrongPassword123") is False


def test_weak_password_is_rejected() -> None:
    """短いパスワードの登録を拒否することを確認します。"""
    service = create_service()
    result = service.register_initial_user("example-user", "short1")
    assert result.success is False


def test_second_initial_user_is_rejected() -> None:
    """初回登録後に別の初回利用者を追加できないことを確認します。"""
    service = create_service()
    service.register_initial_user("first-user", "securePassword123")
    result = service.register_initial_user("second-user", "anotherPassword123")
    assert result.success is False
