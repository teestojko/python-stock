"""株式分析アプリのログイン画面を提供します。"""

import time
import streamlit as st

from src.auth import AuthenticationService, JsonUserRepository, ScryptPasswordHasher

# ログイン試行を許可する最大回数です。
MAX_LOGIN_ATTEMPTS = 5
# 試行回数超過後にログインを停止する秒数です。
LOCKOUT_SECONDS = 30


@st.cache_resource
def create_authentication_service() -> AuthenticationService:
    """認証に必要な部品を組み立てて再利用します。"""
    # 利用者情報を保存するリポジトリです。
    repository = JsonUserRepository("data/users.json")
    # パスワードを安全な形式へ変換する部品です。
    hasher = ScryptPasswordHasher()
    return AuthenticationService(repository, hasher)


def initialize_session() -> None:
    """利用者ごとのログイン状態を初期化します。"""
    # 認証済みの利用者名です。
    st.session_state.setdefault("authenticated_username", None)
    # 連続して失敗したログイン回数です。
    st.session_state.setdefault("failed_login_attempts", 0)
    # ログインを再開できる時刻です。
    st.session_state.setdefault("login_locked_until", 0.0)


def show_login(service: AuthenticationService) -> None:
    """ログインフォームと試行回数制限を表示します。"""
    st.title("ログイン")
    # 現在時刻を使って、一時停止中かを判定します。
    remaining_seconds = int(st.session_state.login_locked_until - time.time())
    if remaining_seconds > 0:
        st.error(f"ログイン試行が一時停止されています。約{remaining_seconds + 1}秒後に再試行してください。")
        return

    with st.form("login_form"):
        # 利用者が入力するログイン名です。
        username = st.text_input("ユーザー名", max_chars=64)
        # 入力値を画面に表示しないパスワード欄です。
        password = st.text_input("パスワード", type="password", max_chars=128)
        # フォームを送信したかを示します。
        submitted = st.form_submit_button("ログイン", use_container_width=True)

    if not submitted:
        return
    if service.authenticate(username, password):
        st.session_state.authenticated_username = service.normalize_username(username)
        st.session_state.failed_login_attempts = 0
        st.session_state.login_locked_until = 0.0
        st.rerun()

    st.session_state.failed_login_attempts += 1
    if st.session_state.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
        st.session_state.failed_login_attempts = 0
        st.session_state.login_locked_until = time.time() + LOCKOUT_SECONDS
    # 利用者の存在を推測できないよう、失敗理由は共通にします。
    st.error("ユーザー名またはパスワードが正しくありません。")


def show_initial_registration(service: AuthenticationService) -> None:
    """利用者が未登録の場合だけ最初のアカウントを作成します。"""
    st.title("初回アカウント登録")
    st.info("最初に管理用アカウントを1件登録してください。")
    with st.form("registration_form", clear_on_submit=True):
        # 新しく登録するログイン名です。
        username = st.text_input("ユーザー名", max_chars=64)
        # 新しく登録するパスワードです。
        password = st.text_input("パスワード（12文字以上）", type="password", max_chars=128)
        # 入力間違いを防ぐ確認用パスワードです。
        confirmation = st.text_input("パスワード（確認）", type="password", max_chars=128)
        # 登録処理を開始したかを示します。
        submitted = st.form_submit_button("アカウントを作成", use_container_width=True)

    if not submitted:
        return
    if password != confirmation:
        st.error("確認用パスワードが一致しません。")
        return
    # 登録結果の詳細は、必要以上の内部情報を画面へ出しません。
    result = service.register_initial_user(username, password)
    if result.success:
        st.success("アカウントを作成しました。ログインしてください。")
        st.rerun()
    else:
        st.error(result.message)


def show_protected_page() -> None:
    """ログインした利用者だけが閲覧できる画面を表示します。"""
    st.title("株式分析アプリ")
    st.success("ログインしました。")
    st.write(f"ログイン中: {st.session_state.authenticated_username}")
    if st.button("ログアウト"):
        st.session_state.authenticated_username = None
        st.rerun()


def main() -> None:
    """登録状態と認証状態に応じて画面を切り替えます。"""
    st.set_page_config(page_title="株式分析アプリ", page_icon="🔐")
    initialize_session()
    # 画面から認証処理を分離したサービスです。
    service = create_authentication_service()
    if not service.has_users():
        show_initial_registration(service)
    elif st.session_state.authenticated_username is None:
        show_login(service)
    else:
        show_protected_page()


if __name__ == "__main__":
    main()
