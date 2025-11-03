# mini-text GTK4実装

Linux X11デスクトップ環境で、ウィンドウ間のテキスト送受信を支援するGTK4アプリケーション。

**現在のステータス**: Phase 3完了、動作確認済み ✓

## PyQt6実装からの改善点

- **IME統合の解決**: GTK4はfcitx5/mozcと安定して統合できる
- **日本語入力対応**: PyQt6で発生していたIME問題が解決
- **venv環境対応**: システムのPyGObjectを使用することで問題なく動作

## 必要要件

### システム要件
- Python 3.9+
- GTK 4.0+
- xdotool

```bash
sudo apt install xdotool python3-gi gir1.2-gtk-4.0
```

**注**: xclipは不要になりました（GTK4の`Gdk.Clipboard` APIを使用）

### Python依存関係
```bash
# venvは --system-site-packages で作成
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

## インストール

```bash
# システムパッケージのインストール
sudo apt install xdotool python3-gi gir1.2-gtk-4.0

# プロジェクトのセットアップ
cd gtk4
python3 -m venv --system-site-packages venv
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
- **テキスト送信**: 選択したウィンドウにテキストを送信（日本語対応）
- **テキストコピー**: 選択したウィンドウからテキストを取得
- **設定管理**: タイミング設定をGUIから変更可能（Phase 4で実装）

## テスト

```bash
source venv/bin/activate
pytest tests/ -v
```

**テスト結果**: 全32テスト成功

## 設定ファイル

`$HOME/.config/mini-text/config.json`

PyQt6実装と設定ファイルを共有できます。

## 開発状況

- [x] Phase 1: 基盤構築 (完了)
- [x] Phase 2: サービスレイヤー実装 (完了)
- [x] Phase 3: 基本UI実装 (完了・動作確認済み ✓)
- [ ] Phase 4: 設定機能実装
- [ ] Phase 5: 改善・テスト

## 動作確認結果

- ✓ アプリケーション起動成功
- ✓ **IME/日本語入力が正常動作**（fcitx5/mozc）
- ✓ テキスト送信機能動作（Inkscapeで確認）
- ✓ テキストコピー機能動作（Inkscapeで確認）
- ✓ ウィンドウリスト表示・更新
- ✓ ウィンドウサイズ保存・復元
- ✓ エラーハンドリング

## 実装の改善

### GTK4ネイティブクリップボードAPIの採用

**背景**: 従来はxclipコマンドを使用していたが、外部依存を削減するためGTK4の`Gdk.Clipboard` APIに移行

**実装**: `GtkClipboardService`を新規作成し、DIP原則に基づいて`TextService`に注入

**メリット**:
- xclip依存の削除（外部コマンド依存が減少）
- より直接的なGTK統合
- プロセス管理の簡素化

**詳細**: `mini_text/services/gtk_clipboard_service.py`参照

### 過去の問題（xclip使用時）

**症状**: テキスト送信時に「クリップボードへのコピーに失敗しました: コマンドがタイムアウトしました」エラー

**原因**: xclipはクリップボード所有権を保持し続けるためプロセスが終了せず、`subprocess.run()`が待機し続ける

**旧解決策**: `subprocess.Popen()`でバックグラウンド起動（現在はGTK4 APIを使用）

## ドキュメント

- `TESTING.md` - Phase 3動作確認手順
- `docs/design/gtk4-detailed-design.md` - GTK4詳細設計書
- `docs/design/application-idea.md` - アプリケーションアイディア（共通）

## アーキテクチャ

SOLID原則に基づいた設計：

- **設定レイヤー**: `ConfigManager` (JSON設定管理)
- **ユーティリティレイヤー**: `X11CommandExecutor`, `DependencyChecker`
- **サービスレイヤー**: `WindowService`, `GtkClipboardService`, `TextService`
- **UIレイヤー**: GTK4ベースの`MainWindow`

PyQt6実装から、サービスレイヤー以下の基本設計を流用していますが、クリップボード実装はGTK4ネイティブAPIに置き換えられています。

## PyQt6実装との比較

| 項目 | PyQt6 | GTK4 |
|------|-------|------|
| IME統合 | ✗ 動作しない | ✓ 正常動作 |
| 日本語入力 | ✗ 不可 | ✓ 可能 |
| venv環境 | △ 問題あり | ✓ 問題なし |
| UIデザインツール | Qt Designer | Glade |
| テストフレームワーク | unittest | pytest |
| 依存関係管理 | pip完結 | システムPyGObject必要 |

## ライセンス

MIT License
