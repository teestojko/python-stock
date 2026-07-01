# python-stock

## ログイン機能の起動

仮想環境を有効にした後、次のコマンドでアプリを起動します。

```
python -m streamlit run app.py
```

初回だけアカウント登録画面が表示されます。ユーザー名と12文字以上のパスワードを登録し、その後ログインしてください。利用者情報はローカルのデータ領域に保存され、パスワードそのものは保存されません。

テストは次のコマンドで実行します。

```
python -m pytest
```

## 環境構築実行手順

1. 開発ツールを準備する（ユーザーのホームディレクトリで実行）

```
xcode-select --install
```

2. Python 3.12をインストールする（brewが未インストールの場合はbrewインストールを先に）

```
brew install python@3.12 git
```

3. 各自プロジェクトフォルダへ移動

4. Python仮想環境を作る

```
python3.12 -m venv .venv
```

・有効化
```
source .venv/bin/activate
```

※仮想環境を終了するときはこちらを実行（再開時は有効化を再度実行）

```
deactivate
```

5. 必要なライブラリをインストールする

・インストール機能を更新
```
python -m pip install --upgrade pip setuptools wheel
```

・基本ライブラリをまとめてインストール
```
python -m pip install \
  streamlit \
  yfinance \
  pandas \
  numpy \
  scikit-learn \
  plotly \
  joblib \
  python-dotenv \
  pytest \
  ruff
```

6. インストールを確認する

```
python -c "import streamlit, yfinance, pandas, sklearn, plotly; print('環境構築成功！')"
```
（ターミナルで「環境構築成功！」と表示されればOK）

・Streamlit自体も動かしてみる（ブラウザにデモ画面が表示される）
```
python -m streamlit hello
```

（拡張機能を追加）
Python（Microsoft）
Pylance
Ruff

・コマンドパレットから次を選ぶ
「Python: Select Interpreter」
・選択後、以下ディレクトリを指定
「プロジェクト名/.venv/bin/python」

10. ライブラリ構成を保存する（環境構築が完了したら、現在のバージョンを保存）

```
python -m pip freeze > requirements.txt
```

※別のPCでは次のコマンドで同じ環境を復元できます
```
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```
