# mini-text

Linux X11デスクトップ環境で、ウィンドウ間のテキスト送受信を支援するアプリケーション。

**現在のステータス**: GTK4実装がPhase 5完了、完全動作（推奨） ✓

## 実装バージョン

### GTK4実装（推奨） ✓

- **ステータス**: Phase 5完了、完全動作
- **場所**: `gtk4/`
- **IME/日本語**: ✓ 動作
- **設定機能**: ✓ 実装済み
- **依存**: xdotool, GTK4 (xclip不要)

```bash
cd gtk4
sudo apt install xdotool python3-gi gir1.2-gtk-4.0
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

詳細: `gtk4/README.md`

### PyQt6実装（中断）

- **ステータス**: Phase 3完了、但しIME動作せず
- **場所**: `pyqt/`
- **IME/日本語**: ✗ 動作しない
- **理由**: venv環境でのIME統合問題

詳細: `pyqt/README.md`, `docs/design/pyqt/ime-integration-issue.md`

## クイックスタート（GTK4推奨）

```bash
cd gtk4
source venv/bin/activate  # 初回は上記インストール手順を実行
python main.py
```

## 機能

- **ウィンドウ一覧表示**: デスクトップ上の全ウィンドウをリスト表示
- **テキスト送信**: 選択したウィンドウにテキストを送信（日本語対応）
- **テキストコピー**: 選択したウィンドウからテキストを取得（日本語対応）
- **IME統合**: fcitx5/mozcと統合（GTK4実装）
- **設定管理**: タイミング設定をJSON設定ファイルで管理

## テスト（GTK4）

```bash
cd gtk4
source venv/bin/activate
pytest tests/ -v
```

**テスト結果**: 全27テスト成功

## 設定ファイル

`$HOME/.config/mini-text/config.json`

両実装（GTK4/PyQt6）で共有されます。

## 開発状況（GTK4実装）

- [x] Phase 1: 基盤構築 (完了)
- [x] Phase 2: サービスレイヤー実装 (完了)
- [x] Phase 3: 基本UI実装 (完了・動作確認済み ✓)
- [x] Phase 3.5: GTK4クリップボードAPI移行 (完了 ✓)
- [x] Phase 4: 設定機能実装 (完了・動作確認済み ✓)
- [x] Phase 5: コードクリーンアップ (完了 ✓)
- [ ] Phase 6: UI/UX改善・ドキュメント整備 (計画中)

## 技術的ハイライト（GTK4実装）

- **SOLID原則**: サービスレイヤーの分離により、UI層とビジネスロジックが独立
- **GTK4ネイティブAPI**: `Gdk.Clipboard`を使用し、xclip依存を削除
- **IME完全統合**: fcitx5/mozcと問題なく動作
- **pytest**: クリーンで保守性の高いテスト

## ドキュメント

### 共通
- `docs/design/application-idea.md` - アプリケーションアイディア
- `CLAUDE.md` - Claude Codeのためのプロジェクト概要

### GTK4実装
- `gtk4/README.md` - GTK4実装の概要
- `gtk4/TESTING.md` - 動作確認手順
- `docs/design/gtk4-detailed-design.md` - GTK4詳細設計書

### PyQt6実装（参考）
- `pyqt/README.md` - PyQt6実装の概要
- `docs/design/pyqt/detailed-design.md` - PyQt6詳細設計書
- `docs/design/pyqt/ime-integration-issue.md` - IME統合の問題と解決策

## ライセンス

MIT License
