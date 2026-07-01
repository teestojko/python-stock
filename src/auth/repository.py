"""利用者情報をローカルJSONファイルへ保存します。"""

import json
import os
import threading
from pathlib import Path
from typing import Any

from .models import User


class JsonUserRepository:
    """利用者情報を権限を制限したJSONファイルで管理します。"""

    def __init__(self, file_path: str | Path) -> None:
        # 利用者情報を保存するファイルの場所です。
        self._file_path = Path(file_path)
        # 同一プロセス内の同時更新を防ぐためのロックです。
        self._lock = threading.Lock()

    def has_users(self) -> bool:
        """保存済みの利用者が存在するか確認します。"""
        return bool(self._read_users())

    def find_by_username(self, username: str) -> User | None:
        """完全一致する利用者を検索します。"""
        for stored_user in self._read_users():
            if stored_user.get("username") == username:
                return User(username=username, password_hash=stored_user["password_hash"])
        return None

    def add_initial_user(self, user: User) -> bool:
        """未登録時だけ最初の利用者を安全に保存します。"""
        with self._lock:
            if self._read_users():
                return False
            self._write_users([{"username": user.username, "password_hash": user.password_hash}])
            return True

    def _read_users(self) -> list[dict[str, str]]:
        """保存ファイルを検証しながら読み込みます。"""
        if not self._file_path.exists():
            return []
        try:
            # ファイルサイズを制限して異常な資源消費を防ぎます。
            if self._file_path.stat().st_size > 1_000_000:
                return []
            with self._file_path.open("r", encoding="utf-8") as file:
                loaded_data: Any = json.load(file)
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(loaded_data, list):
            return []
        # 想定した文字列項目だけを持つデータに限定します。
        return [
            item for item in loaded_data
            if isinstance(item, dict)
            and isinstance(item.get("username"), str)
            and isinstance(item.get("password_hash"), str)
        ]

    def _write_users(self, users: list[dict[str, str]]) -> None:
        """途中状態を残さないよう、一時ファイル経由で保存します。"""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        # 不完全な書き込みを防ぐ同一ディレクトリ内の一時ファイルです。
        temporary_path = self._file_path.with_suffix(".tmp")
        file_descriptor = os.open(temporary_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as file:
                json.dump(users, file, ensure_ascii=False)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_path, self._file_path)
            os.chmod(self._file_path, 0o600)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()
