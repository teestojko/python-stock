"""認証機能で扱うデータ構造を定義します。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """保存する利用者情報を表します。"""

    # 大文字小文字などを統一した利用者名です。
    username: str
    # 平文を保存しないためのパスワードハッシュです。
    password_hash: str


@dataclass(frozen=True)
class RegistrationResult:
    """初回登録の結果を表します。"""

    # 登録に成功したかを示します。
    success: bool
    # 利用者に伝える安全な結果メッセージです。
    message: str
