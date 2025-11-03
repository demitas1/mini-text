# mini-text GTK4実装 詳細設計書

**最終更新**: 2025-11-03

## 概要

mini-textは、Linux X11デスクトップ環境で動作する、ウィンドウ間のテキスト送受信を支援するGTK4アプリケーションです。

PyQt6実装からGTK4に移植することで、IME（日本語入力）統合の問題を解決します。

## PyQt6実装からの変更点

### 解決される問題
- **IME統合**: GTK4はシステムのIMフレームワーク（fcitx5/mozc）と安定して統合できる
- **依存関係管理**: PyGObjectはpip経由でインストール可能、venv環境でも問題なし

### 継承する設計
- サービスレイヤー（`WindowService`, `ClipboardService`, `TextService`）
- ユーティリティレイヤー（`X11CommandExecutor`, `DependencyChecker`）
- 設定管理（`ConfigManager`）
- SOLID原則に基づいたアーキテクチャ

## 仕様

### 機能要件

PyQt6実装と同一の機能を提供:

1. **ウィンドウ一覧表示**: X11デスクトップ上の全ウィンドウをリストボックスに表示
   - リフレッシュボタンで手動更新
   - 表示形式: ウィンドウID + ウィンドウ名

2. **テキスト送信(typeinto)**: テキストボックスに入力した文字列を選択したウィンドウに送信
   - クリップボード経由でCtrl+Vで貼り付け
   - 複数行対応
   - 日本語対応（IME統合）

3. **テキストコピー(copyfrom)**: 選択したウィンドウからテキストを取得
   - ボタン押下後、設定時間ウェイト
   - ユーザーが手動でテキストボックスをクリック
   - Ctrl+A → Ctrl+C で自動取得
   - 複数行対応

4. **設定管理**:
   - ウィンドウサイズ(デフォルト: 800x600)
   - 各種ウェイト時間をconfigファイルで管理
   - メニューから設定ダイアログで変更可能

5. **エラーハンドリング**:
   - 起動時: xdotool/xclipのインストールチェック → 未インストールならエラーダイアログ表示して終了
   - 実行時: エラー内容をステータスバーに表示

6. **常に最前面**: アプリケーションウィンドウは常に最前面に表示

### 技術要件

- Python 3.9+
- GTK 4.0+
- PyGObject (python3-gi) - pip経由でインストール
- Glade 4.0+ (.uiファイルでUI設計、オプション)
- xdotool, xclip (外部依存)
- Linux X11環境

## アーキテクチャ

### プロジェクト構成

```
gtk4/
├── main.py                          # エントリーポイント
├── requirements.txt                 # Python依存関係 (PyGObject, pytest)
├── mini_text/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config_manager.py        # 設定ファイル管理(JSON形式) ※PyQt6から流用
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── x11_command_executor.py  # xdotool/xclip実行 ※PyQt6から流用
│   │   └── dependency_checker.py    # xdotool/xclipチェック ※PyQt6から流用
│   ├── services/
│   │   ├── __init__.py
│   │   ├── window_service.py        # ウィンドウ操作 ※PyQt6から流用
│   │   ├── clipboard_service.py     # クリップボード操作(xclip版) ※PyQt6から流用
│   │   ├── gtk_clipboard_service.py # クリップボード操作(GTK4版) ※新規実装
│   │   └── text_service.py          # テキスト送受信統合 ※PyQt6から流用
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py           # メインウィンドウ (GTK4用に新規実装)
│       ├── settings_dialog.py       # 設定ダイアログ (GTK4用に新規実装)
│       └── resources/
│           ├── main_window.ui       # Glade形式UIファイル
│           └── settings_dialog.ui   # Glade形式UIファイル
└── tests/                           # pytest形式のテスト
    ├── __init__.py
    ├── conftest.py                  # pytest設定
    ├── test_dependency_checker.py   # ※PyQt6から流用・修正
    ├── test_x11_command_executor.py # ※PyQt6から流用・修正
    ├── test_config_manager.py       # ※PyQt6から流用・修正
    ├── test_window_service.py       # ※PyQt6から流用・修正
    ├── test_clipboard_service.py    # ※PyQt6から流用・修正
    ├── test_gtk_clipboard_service.py # ※手動テストのみ
    └── test_text_service.py         # ※PyQt6から流用・修正
```

**設定ファイル保存先**: `$HOME/.config/mini-text/config.json` (PyQt6実装と共通)

### SOLID原則の適用

PyQt6実装と同一:

- **SRP (Single Responsibility Principle)**: 各Serviceクラスは単一の責務
- **OCP (Open/Closed Principle)**: Executor抽象化により拡張が容易
- **DIP (Dependency Inversion Principle)**: TextServiceは抽象Executorに依存

## GTK4固有の設計

### UIファイルの扱い

**Glade形式（GtkBuilder）を使用**:

```python
# main_window.py
from gi.repository import Gtk

@Gtk.Template(filename='mini_text/ui/resources/main_window.ui')
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    # UIエレメントをテンプレートからバインド
    window_list = Gtk.Template.Child()
    text_view = Gtk.Template.Child()
    send_button = Gtk.Template.Child()
    # ...
```

**UIファイル作成方法**:
1. **オプション1**: Gladeエディタで視覚的に作成
2. **オプション2**: XMLを直接記述（Gladeがない環境でも可）

### ウィジェット対応表

PyQt6 → GTK4のウィジェット変換:

| 機能 | PyQt6 | GTK4 |
|------|-------|------|
| メインウィンドウ | QMainWindow | Gtk.ApplicationWindow |
| リストボックス | QListWidget | Gtk.ListView または Gtk.ListBox |
| テキストエディタ | QPlainTextEdit | Gtk.TextView (+ Gtk.TextBuffer) |
| ボタン | QPushButton | Gtk.Button |
| ステータスバー | QStatusBar | Gtk.Statusbar または Gtk.Label |
| メニューバー | QMenuBar | Gtk.MenuBar または GMenu |
| ダイアログ | QDialog | Gtk.Dialog |
| レイアウト | QVBoxLayout, QHBoxLayout | Gtk.Box (orientation指定) |
| スプリッター | QSplitter | Gtk.Paned |

### アプリケーションエントリーポイント

GTK4では`Gtk.Application`を使用:

```python
# main.py
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

class MiniTextApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.example.minitext')
        # サービスの初期化

    def do_activate(self):
        # メインウィンドウを作成・表示
        win = MainWindow(application=self, ...)
        win.present()

if __name__ == '__main__':
    app = MiniTextApplication()
    app.run(sys.argv)
```

### 常に最前面の実装

GTK4での実装:

```python
# ウィンドウを常に最前面に設定
window.set_keep_above(True)
```

### ステータスバーの扱い

GTK4の`Gtk.Statusbar`は使いにくいため、`Gtk.Label`での代用も検討:

```python
# オプション1: Gtk.Statusbar
statusbar = Gtk.Statusbar()
context_id = statusbar.get_context_id("main")
statusbar.push(context_id, "メッセージ")

# オプション2: Gtk.Label (シンプル)
status_label = Gtk.Label(label="メッセージ")
status_label.set_halign(Gtk.Align.START)
```

## クリップボード実装の移行計画

### 背景

現在の実装ではxclipコマンドを使用してクリップボード操作を行っていますが、GTK4には`Gdk.Clipboard` APIが用意されており、外部コマンドへの依存を削減できます。

### GTK4 Gdk.Clipboard API概要

#### 取得方法

```python
import gi
gi.require_version('Gdk', '4.0')
from gi.repository import Gdk

# デフォルトディスプレイからクリップボードを取得
display = Gdk.Display.get_default()
clipboard = display.get_clipboard()  # CLIPBOARD selection
# または
primary_clipboard = display.get_primary_clipboard()  # PRIMARY selection
```

#### 書き込み（同期）

```python
# テキストをクリップボードにコピー
clipboard.set(text)  # 同期的に実行可能
```

#### 読み込み（非同期のみ）

```python
# コールバック方式
def on_read_finish(_clipboard, async_result):
    text = clipboard.read_text_finish(async_result)
    if text is not None:
        # テキスト処理
        pass

clipboard.read_text_async(None, on_read_finish)
```

### 実装方針

#### GtkClipboardServiceの作成

新しい`GtkClipboardService`を作成し、既存の`ClipboardService`インターフェースを維持します（DIP原則）。

```python
"""GTK4 Gdk.Clipboardを使用したクリップボードサービス"""
from typing import Optional
import gi
gi.require_version('Gdk', '4.0')
from gi.repository import Gdk, GLib


class GtkClipboardService:
    """GTK4 Gdk.Clipboardを使用したクリップボード操作サービス"""

    def __init__(self, clipboard: Optional[Gdk.Clipboard] = None):
        """
        Args:
            clipboard: Gdk.Clipboardインスタンス（Noneの場合はデフォルトを使用）
        """
        if clipboard is None:
            display = Gdk.Display.get_default()
            self.clipboard = display.get_clipboard()
        else:
            self.clipboard = clipboard

    def copy_to_clipboard(self, text: str) -> tuple[bool, str]:
        """
        クリップボードにテキストをコピー（同期）

        Args:
            text: コピーするテキスト

        Returns:
            tuple[bool, str]: (成功したか, エラーメッセージ)
        """
        try:
            self.clipboard.set(text)
            return True, ""
        except Exception as e:
            return False, f"クリップボードへのコピーに失敗しました: {str(e)}"

    def get_from_clipboard(self) -> tuple[bool, str, str]:
        """
        クリップボードからテキストを取得（同期）

        注意: GTK4のAPIは非同期のみだが、GLib.MainContextを使用して同期的に待機

        Returns:
            tuple[bool, str, str]: (成功したか, テキスト, エラーメッセージ)
        """
        try:
            # 結果を格納する変数
            result = {"text": None, "error": None}

            def on_read_finish(_clipboard, async_result):
                """非同期読み込み完了時のコールバック"""
                try:
                    text = self.clipboard.read_text_finish(async_result)
                    result["text"] = text if text is not None else ""
                except Exception as e:
                    result["error"] = str(e)

            # 非同期読み込み開始
            self.clipboard.read_text_async(None, on_read_finish)

            # メインループで結果を待機
            context = GLib.MainContext.default()
            while result["text"] is None and result["error"] is None:
                context.iteration(True)

            if result["error"]:
                return False, "", f"クリップボードからの取得に失敗しました: {result['error']}"

            return True, result["text"], ""

        except Exception as e:
            return False, "", f"クリップボードからの取得に失敗しました: {str(e)}"
```

#### 依存性注入の変更

`main.py`で`GtkClipboardService`を使用:

```python
from mini_text.services.gtk_clipboard_service import GtkClipboardService

# アプリケーション初期化時
display = Gdk.Display.get_default()
clipboard = display.get_clipboard()
clipboard_service = GtkClipboardService(clipboard)
text_service = TextService(window_service, clipboard_service, executor)
```

#### TextServiceの変更は不要

`TextService`は抽象的な`clipboard_service`に依存しているため（DIP原則）、注入するサービスを変更するだけで動作します。

### メリット

1. **外部依存の削減**: xclipコマンドへの依存がなくなる
2. **シンプルな実装**: バックグラウンドプロセス管理が不要
3. **GTK統合**: ネイティブなGTK4機能を使用
4. **保守性向上**: Pythonコードのみで完結

### 注意点

1. **非同期処理**:
   - GTK4の読み込みAPIは非同期のみ
   - `GLib.MainContext`で同期的に待機する実装を採用
   - UIスレッドをブロックする可能性があるが、クリップボード読み込みは高速なため実用上問題なし

2. **クリップボード所有権**:
   - GTK4は自動的にクリップボード所有権を管理
   - xclipのような明示的なバックグラウンドプロセスは不要
   - アプリケーション終了後もクリップボードは保持される（GTK4の仕様）

3. **テスト**:
   - GTK環境が必要なため、単体テストが複雑化
   - 複雑なセットアップが必要なテストは手動で実施

### 移行状況

✅ **完了** (2025-11-03)

1. ✅ **Phase 1**: `GtkClipboardService`を新規作成
2. ✅ **Phase 2**: `main.py`で`GtkClipboardService`を使用するように変更
3. ✅ **Phase 3**: 実際の環境で手動テスト（日本語テキストを含む）
   - テキスト送信機能: 正常動作
   - テキストコピー機能: 正常動作
   - 日本語テキスト: 正常動作
   - 既存テスト32件: 全て成功

### 現在の状態

xclip依存は実質的に削除されました：
- ✅ `GtkClipboardService`が実装され、使用されている
- ✅ `main.py`は`GtkClipboardService`を注入
- ✅ README, CLAUDE.md, TESTING.mdからxclip依存を削除
- ⚠️ レガシーコードが残存（参考用、削除可能）:
  - `mini_text/services/clipboard_service.py` (xclip版、未使用)
  - `mini_text/utils/x11_command_executor.py` (xclip特殊処理含む)
  - `DependencyChecker` (xclipチェック含む)

## クラス設計

### UIレイヤー以外はPyQt6と同一

`ConfigManager`, `X11CommandExecutor`, `DependencyChecker`, `WindowService`, ~~`ClipboardService`~~, `TextService`の設計はPyQt6実装のドキュメント（`docs/design/pyqt/detailed-design.md`）を参照。

**注意**: `ClipboardService`は上記の`GtkClipboardService`に置き換えられます。

### GTK4 UI実装

#### MainWindow (ui/main_window.py)

```python
@Gtk.Template(filename='mini_text/ui/resources/main_window.ui')
class MainWindow(Gtk.ApplicationWindow):
    """メインウィンドウ"""

    __gtype_name__ = 'MainWindow'

    # UIエレメント（.uiファイルからバインド）
    window_list = Gtk.Template.Child()      # Gtk.ListBox
    text_buffer = None                      # Gtk.TextBuffer (コードで取得)
    text_view = Gtk.Template.Child()        # Gtk.TextView
    send_button = Gtk.Template.Child()      # Gtk.Button
    copy_button = Gtk.Template.Child()      # Gtk.Button
    refresh_button = Gtk.Template.Child()   # Gtk.Button
    status_label = Gtk.Template.Child()     # Gtk.Label

    def __init__(self, application, text_service, window_service, config_manager):
        super().__init__(application=application)

        self.text_service = text_service
        self.window_service = window_service
        self.config_manager = config_manager

        # テキストバッファを取得
        self.text_buffer = self.text_view.get_buffer()

        # ウィンドウサイズを復元
        width, height = self.config_manager.get_window_size()
        self.set_default_size(width, height)

        # 常に最前面に設定
        self.set_keep_above(True)

        # シグナル接続
        self.connect_signals()

        # 初回のウィンドウリスト取得
        self.refresh_window_list()

    def connect_signals(self):
        """シグナルとハンドラを接続"""
        self.refresh_button.connect('clicked', self.on_refresh_clicked)
        self.send_button.connect('clicked', self.on_send_clicked)
        self.copy_button.connect('clicked', self.on_copy_clicked)
        self.connect('close-request', self.on_close_request)

    def refresh_window_list(self):
        """ウィンドウ一覧を更新"""
        # ListBoxをクリア
        while True:
            row = self.window_list.get_row_at_index(0)
            if row is None:
                break
            self.window_list.remove(row)

        # ウィンドウ一覧を取得
        windows = self.window_service.get_window_list()

        # リストに追加
        for window_id, window_name in windows:
            label = Gtk.Label(label=f"{window_id}: {window_name}")
            label.set_halign(Gtk.Align.START)
            self.window_list.append(label)

        self.show_status(f"ウィンドウリストを更新しました ({len(windows)}件)")

    def on_refresh_clicked(self, button):
        """リフレッシュボタンクリック時の処理"""
        self.refresh_window_list()

    def on_send_clicked(self, button):
        """送信ボタンクリック時の処理"""
        # 選択されているウィンドウを取得
        selected_row = self.window_list.get_selected_row()
        if not selected_row:
            self.show_status("ウィンドウを選択してください", is_error=True)
            return

        # テキストを取得
        start_iter = self.text_buffer.get_start_iter()
        end_iter = self.text_buffer.get_end_iter()
        text = self.text_buffer.get_text(start_iter, end_iter, False)

        if not text:
            self.show_status("送信するテキストを入力してください", is_error=True)
            return

        # ウィンドウIDを取得
        label = selected_row.get_child()
        window_id = label.get_label().split(":")[0]

        # 設定から待機時間を取得
        activate_wait = self.config_manager.get_timing("window_activate_wait")
        key_wait = self.config_manager.get_timing("key_input_wait")

        # テキストを送信
        success, error_msg = self.text_service.send_text(
            window_id, text, activate_wait, key_wait
        )

        if success:
            self.show_status("テキストを送信しました")
        else:
            self.show_status(f"エラー: {error_msg}", is_error=True)

    def on_copy_clicked(self, button):
        """コピーボタンクリック時の処理"""
        # 設定から待機時間を取得
        copyfrom_wait = self.config_manager.get_timing("copyfrom_wait")
        key_wait = self.config_manager.get_timing("key_input_wait")

        # ユーザーに通知
        self.show_status(
            f"{copyfrom_wait}秒後にコピーを開始します。対象のテキストボックスをクリックしてください"
        )

        # GLibのタイムアウトを使用して非同期実行
        GLib.timeout_add_seconds(int(copyfrom_wait), self._do_copy, key_wait)

    def _do_copy(self, key_wait):
        """コピー実行（タイムアウトコールバック）"""
        # テキストを取得
        success, text, error_msg = self.text_service.receive_text(key_wait)

        if success:
            # テキストバッファに設定
            self.text_buffer.set_text(text)
            self.show_status("テキストをコピーしました")
        else:
            self.show_status(f"エラー: {error_msg}", is_error=True)

        return False  # タイムアウトを一回限りにする

    def show_status(self, message: str, is_error: bool = False):
        """ステータスメッセージを表示"""
        self.status_label.set_label(message)

        # エラーの場合は色を変更
        if is_error:
            self.status_label.add_css_class('error')
        else:
            self.status_label.remove_css_class('error')

    def on_close_request(self, window):
        """ウィンドウクローズ時の処理"""
        # ウィンドウサイズを保存
        width = self.get_width()
        height = self.get_height()
        self.config_manager.set_window_size(width, height)
        self.config_manager.save_config()

        return False  # クローズを許可
```

#### SettingsDialog (ui/settings_dialog.py)

Phase 4で実装。基本構造はMainWindowと同様。

## 設定ファイル仕様

PyQt6実装と同一。`$HOME/.config/mini-text/config.json`を使用。

## テスト戦略

### pytest使用

PyQt6実装のunittestベーステストをpytest形式に変換:

```python
# tests/test_config_manager.py (pytest形式)
import pytest
from pathlib import Path
from mini_text.config.config_manager import ConfigManager

@pytest.fixture
def temp_config_file(tmp_path):
    """一時設定ファイルのフィクスチャ"""
    config_file = tmp_path / "config.json"
    return str(config_file)

def test_default_config(temp_config_file):
    """デフォルト設定のテスト"""
    manager = ConfigManager(temp_config_file)
    width, height = manager.get_window_size()
    assert width == 800
    assert height == 600

def test_save_and_load_config(temp_config_file):
    """設定の保存と読み込みのテスト"""
    manager = ConfigManager(temp_config_file)
    manager.set_window_size(1024, 768)
    manager.save_config()

    # 新しいインスタンスで読み込み
    manager2 = ConfigManager(temp_config_file)
    width, height = manager2.get_window_size()
    assert width == 1024
    assert height == 768
```

### テスト範囲

- **ユニットテスト**: サービスレイヤー、ユーティリティレイヤー（PyQt6から流用）
- **統合テスト**: 必要に応じて追加
- **UIテスト**: 手動テスト（Phase 3-5で実施）

## 実装計画

### Phase 1: 基盤構築

1. プロジェクト構造作成
   - `gtk4/`ディレクトリ構造
   - `requirements.txt` (PyGObject, pytest)
   - `.gitignore`更新

2. PyQt6からファイルコピー
   - `config/config_manager.py`
   - `utils/x11_command_executor.py`
   - `utils/dependency_checker.py`
   - 各`__init__.py`

3. pytestテスト移植
   - unittestからpytest形式に変換
   - `conftest.py`作成
   - 全テスト実行・確認

### Phase 2: サービスレイヤー実装

1. PyQt6からサービスクラスをコピー
   - `services/window_service.py`
   - `services/clipboard_service.py`
   - `services/text_service.py`

2. pytestテスト移植
   - サービスレイヤーのテストをpytest形式に変換
   - 全テスト実行・確認

### Phase 3: 基本UI実装

1. Glade UIファイル作成
   - `ui/resources/main_window.ui` (XML直接作成またはGlade使用)
   - 必要なウィジェット配置

2. MainWindow実装
   - `ui/main_window.py`
   - GtkBuilder統合
   - シグナル接続
   - 各機能実装

3. main.py実装
   - `Gtk.Application`ベースのエントリーポイント
   - 依存関係チェック
   - サービスインスタンス生成

4. 動作確認
   - アプリケーション起動
   - 全機能テスト（日本語入力含む）

### Phase 4: 設定機能実装

1. 設定ダイアログUI作成
   - `ui/resources/settings_dialog.ui`

2. SettingsDialog実装
   - `ui/settings_dialog.py`

3. メニュー統合

### Phase 5: 改善・テスト

1. エラーハンドリング強化
2. UI/UX改善
3. ドキュメント更新
4. 統合テスト

## 依存関係

### requirements.txt

```
PyGObject>=3.42.0
pytest>=7.0.0
pytest-cov>=3.0.0
```

### システム依存

```bash
# GTK4開発ライブラリ（PyGObjectビルドに必要）
sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0

# ランタイム依存
sudo apt install xdotool
# 注: xclipは将来的にGtkClipboardServiceへの移行後に不要になる予定

# Glade（オプション、UIファイル編集用）
sudo apt install glade
```

## PyQt6実装との互換性

- **設定ファイル**: 同一パス(`~/.config/mini-text/config.json`)を使用、相互運用可能
- **コア機能**: 同一の動作を保証
- **データ**: 互換性あり

## 期待される成果

1. **IME統合の解決**: 日本語入力が正常に動作
2. **venv環境での動作**: pip経由のPyGObjectで問題なし
3. **SOLID原則の継承**: 保守性の高いコード
4. **テストカバレッジ**: pytestによる包括的テスト

## 参考情報

- [GTK4ドキュメント](https://docs.gtk.org/gtk4/)
- [PyGObjectドキュメント](https://pygobject.readthedocs.io/)
- [Gladeドキュメント](https://glade.gnome.org/)
- [Python GTK+ 3 Tutorial](https://python-gtk-3-tutorial.readthedocs.io/) (GTK3だが参考になる)
