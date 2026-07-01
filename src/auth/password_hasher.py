"""標準ライブラリのscryptでパスワードを安全に処理します。"""

import base64
import hashlib
import hmac
import os


class ScryptPasswordHasher:
    """ランダムな値を用いてパスワードをハッシュ化します。"""

    # scryptで使用するCPU・メモリコストの値です。
    _N = 2**14
    # scryptで使用するブロックサイズです。
    _R = 8
    # scryptで使用する並列化係数です。
    _P = 1
    # 生成するハッシュ値のバイト数です。
    _KEY_LENGTH = 32

    def hash(self, password: str) -> str:
        """ランダムなソルトを使い、パスワードを保存用文字列へ変換します。"""
        # 同じパスワードでも異なる結果にするランダムなソルトです。
        salt = os.urandom(16)
        # 総当たり攻撃を難しくする計算結果です。
        derived_key = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=self._N, r=self._R, p=self._P, dklen=self._KEY_LENGTH
        )
        return "$".join((
            "scrypt", str(self._N), str(self._R), str(self._P),
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(derived_key).decode("ascii"),
        ))

    def verify(self, password: str, encoded_password: str) -> bool:
        """保存値を解析し、一定時間比較でパスワードを検証します。"""
        try:
            # 保存形式からアルゴリズムと計算条件を取り出します。
            algorithm, n_value, r_value, p_value, salt_value, hash_value = encoded_password.split("$")
            if algorithm != "scrypt":
                return False
            # 改ざんされた過大な値による資源消費を防ぎます。
            if (int(n_value), int(r_value), int(p_value)) != (self._N, self._R, self._P):
                return False
            salt = base64.b64decode(salt_value, validate=True)
            expected_key = base64.b64decode(hash_value, validate=True)
            if len(salt) != 16 or len(expected_key) != self._KEY_LENGTH:
                return False
            actual_key = hashlib.scrypt(
                password.encode("utf-8"), salt=salt, n=self._N, r=self._R, p=self._P, dklen=self._KEY_LENGTH
            )
            return hmac.compare_digest(actual_key, expected_key)
        except (ValueError, TypeError):
            # 壊れた保存値を認証失敗として安全に扱います。
            return False
