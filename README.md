# mini-text

Linux X11デスクトップ環境で、ウィンドウ間のテキスト送受信を支援するPyQt6アプリケーション。

**現在のステータス**: Phase 3実装完了（基本UI動作確認済み、IME統合に既知の問題あり）

## 必要要件

- Python 3.9+
- xdotool
- xclip
- PyQt6 6.6.0+

```bash
sudo apt install xdotool xclip
```

## インストール

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 実行

```bash
source venv/bin/activate
python main.py
```

## 機能

- **ウィンドウ一覧表示**: デスクトップ上の全ウィンドウをリスト表示
- **テキスト送信**: 選択したウィンドウにテキストを送信
- **テキストコピー**: 選択したウィンドウからテキストを取得
- **設定管理**: タイミング設定をGUIから変更可能

## テスト

```bash
source venv/bin/activate
python -m unittest discover -s tests -v
```

**テスト結果**: 全32テスト成功

## 設定ファイル

`$HOME/.config/mini-text/config.json`

## 既知の問題

### IME（日本語入力）が動作しない

venv環境のPyQt6とシステムのfcitx5プラグインのバージョン不一致により、IMEが動作しません。

**詳細**: `docs/design/ime-integration-issue.md`を参照

**回避策**:
- システムのPyQt6を使用する（`--system-site-packages`でvenv作成）
- 英数字のみで動作確認を行う

## 開発状況

- [x] Phase 1: 基盤構築 (完了)
- [x] Phase 2: サービスレイヤー実装 (完了)
- [x] Phase 3: 基本UI実装 (完了 - IME問題あり)
- [ ] Phase 4: 設定機能実装
- [ ] Phase 5: 改善・テスト

## ドキュメント

- `docs/design/application-idea.md` - アプリケーションアイディア
- `docs/design/detailed-design.md` - 詳細設計書
- `docs/design/ime-integration-issue.md` - IME統合の問題と解決策
- `TESTING.md` - Phase 3動作確認手順

## ライセンス

MIT License
