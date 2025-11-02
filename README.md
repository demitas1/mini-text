# mini-text

Linux X11デスクトップ環境で、ウィンドウ間のテキスト送受信を支援するPyQt6アプリケーション。

## 必要要件

- Python 3.9+
- xdotool
- xclip

```bash
sudo apt install xdotool xclip
```

## インストール

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 実行

```bash
python main.py
```

## 機能

- **ウィンドウ一覧表示**: デスクトップ上の全ウィンドウをリスト表示
- **テキスト送信**: 選択したウィンドウにテキストを送信
- **テキストコピー**: 選択したウィンドウからテキストを取得
- **設定管理**: タイミング設定をGUIから変更可能

## テスト

```bash
python -m unittest discover -s tests -v
```

## 設定ファイル

`$HOME/.config/mini-text/config.json`

## ライセンス

MIT License
