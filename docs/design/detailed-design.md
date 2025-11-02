# mini-text 詳細設計書

## 概要

mini-textは、Linux X11デスクトップ環境で動作する、ウィンドウ間のテキスト送受信を支援するPyQt6アプリケーションです。

## 仕様

### 機能要件

1. **ウィンドウ一覧表示**: X11デスクトップ上の全ウィンドウをリストボックスに表示
   - リフレッシュボタンで手動更新
   - 表示形式: ウィンドウID + ウィンドウ名

2. **テキスト送信(typeinto)**: テキストボックスに入力した文字列を選択したウィンドウに送信
   - クリップボード経由でCtrl+Vで貼り付け
   - 複数行対応

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
- PyQt6
- Qt Designer (.uiファイルでUI設計)
- xdotool, xclip (外部依存)
- Linux X11環境

## アーキテクチャ

### プロジェクト構成

```
mini-text/
├── main.py                          # エントリーポイント
├── requirements.txt                 # Python依存関係
├── README.md                        # 使用方法
├── LICENSE.txt                      # MITライセンス
├── .gitignore                       # Git除外設定
├── mini_text/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config_manager.py        # 設定ファイル管理(JSON形式)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── x11_command_executor.py  # xdotool/xclip実行
│   │   └── dependency_checker.py    # xdotool/xclipインストールチェック
│   ├── services/
│   │   ├── __init__.py
│   │   ├── window_service.py        # ウィンドウ操作
│   │   ├── clipboard_service.py     # クリップボード操作
│   │   └── text_service.py          # テキスト送受信統合
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py           # メインウィンドウ
│       ├── settings_dialog.py       # 設定ダイアログ
│       ├── resources/
│       │   ├── main_window.ui       # Qt Designer UIファイル
│       │   └── settings_dialog.ui   # Qt Designer UIファイル
│       └── models.py                # リストモデル(将来的に使用)
├── tests/                           # ユニットテスト
│   ├── __init__.py
│   ├── test_dependency_checker.py
│   ├── test_x11_command_executor.py
│   ├── test_config_manager.py
│   ├── test_window_service.py       # Phase 2で追加
│   ├── test_clipboard_service.py    # Phase 2で追加
│   └── test_text_service.py         # Phase 2で追加
└── docs/
    ├── design/
    │   ├── application-idea.md      # アイディアメモ
    │   └── detailed-design.md       # この設計書
    └── examples/
        ├── typeinto.sh              # コンセプト実証スクリプト
        └── copyfrom.sh              # コンセプト実証スクリプト
```

**設定ファイル保存先**: `$HOME/.config/mini-text/config.json`
- XDG Base Directory仕様に準拠
- ディレクトリが存在しない場合は自動作成

### SOLID原則の適用

- **SRP (Single Responsibility Principle)**: 各Serviceクラスは単一の責務
  - WindowService: ウィンドウ操作のみ
  - ClipboardService: クリップボード操作のみ
  - TextService: テキスト送受信のオーケストレーション

- **OCP (Open/Closed Principle)**: Executor抽象化により、将来Waylandサポート等の拡張が容易

- **LSP (Liskov Substitution Principle)**: 現時点では継承なし

- **ISP (Interface Segregation Principle)**: 各Serviceインターフェースは必要最小限のメソッドのみ提供

- **DIP (Dependency Inversion Principle)**: TextServiceは具体的なX11CommandExecutorに直接依存せず、Executorインターフェースに依存

## 設定ファイル仕様

### config.json

**保存先**: `$HOME/.config/mini-text/config.json`

```json
{
  "window": {
    "width": 800,
    "height": 600
  },
  "timing": {
    "window_activate_wait": 0.3,
    "key_input_wait": 0.3,
    "copyfrom_wait": 3.0
  }
}
```

**説明**:
- `window.width`, `window.height`: メインウィンドウのサイズ
- `timing.window_activate_wait`: ウィンドウアクティベート後のウェイト(秒)
- `timing.key_input_wait`: キー入力間のウェイト(秒)
- `timing.copyfrom_wait`: copyfrom実行前のウェイト(秒) - ユーザーがテキストボックスをクリックする時間

## クラス設計

### 1. ConfigManager (config/config_manager.py)

設定ファイルの読み書きを管理するクラス。JSON形式で`$HOME/.config/mini-text/config.json`に保存。

```python
class ConfigManager:
    """設定ファイルの読み書きを管理 (JSON形式)"""

    def __init__(self, config_path: str = None)
        """
        Args:
            config_path: 設定ファイルのパス (Noneの場合は $HOME/.config/mini-text/config.json)
        """

    def _get_default_config_path(self) -> str
        """デフォルトの設定ファイルパスを取得"""

    def _ensure_config_dir(self) -> None
        """設定ファイルディレクトリが存在しない場合は作成"""

    def load_config(self) -> None
        """設定ファイルを読み込む。ファイルが存在しない場合はデフォルト値を使用"""

    def save_config(self) -> None
        """現在の設定をファイルに保存"""

    def get_window_size(self) -> tuple[int, int]
        """ウィンドウサイズを取得"""

    def set_window_size(self, width: int, height: int) -> None
        """ウィンドウサイズを設定"""

    def get_timing(self, key: str) -> float
        """指定したタイミング設定値を取得
        Args:
            key: "window_activate_wait", "key_input_wait", "copyfrom_wait"
        """

    def set_timing(self, key: str, value: float) -> None
        """指定したタイミング設定値を設定"""

    def get_all_config(self) -> dict
        """全設定を辞書で取得"""
```

### 2. DependencyChecker (utils/dependency_checker.py)

xdotool/xclipのインストール確認を行うユーティリティクラス。

```python
class DependencyChecker:
    """xdotool/xclipのインストール確認"""

    @staticmethod
    def check_dependencies() -> tuple[bool, list[str]]:
        """
        必要な外部コマンドがインストールされているかチェック

        Returns:
            tuple[bool, list[str]]: (全て利用可能か, 不足しているツールのリスト)
        """
```

### 3. X11CommandExecutor (utils/x11_command_executor.py)

xdotool/xclipコマンドを実行する低レベルユーティリティクラス。

```python
class X11CommandExecutor:
    """xdotool/xclipコマンドの実行"""

    @staticmethod
    def execute(command: list[str], input_data: str = None) -> tuple[bool, str, str]:
        """
        コマンドを実行

        Args:
            command: 実行するコマンドと引数のリスト
            input_data: 標準入力に渡すデータ(オプション)

        Returns:
            tuple[bool, str, str]: (成功したか, stdout, stderr)
        """
```

### 4. WindowService (services/window_service.py)

ウィンドウ操作を担当するサービスクラス。

```python
class WindowService:
    """ウィンドウ操作サービス (SRP)"""

    def __init__(self, executor: X11CommandExecutor):
        """
        Args:
            executor: コマンド実行ユーティリティ
        """

    def get_window_list(self) -> list[tuple[str, str]]:
        """
        現在開いているウィンドウの一覧を取得

        Returns:
            list[tuple[str, str]]: [(window_id, window_name), ...]
        """

    def activate_window(self, window_id: str, wait_time: float) -> tuple[bool, str]:
        """
        指定したウィンドウをアクティブ化

        Args:
            window_id: アクティブ化するウィンドウのID
            wait_time: アクティブ化後の待機時間(秒)

        Returns:
            tuple[bool, str]: (成功したか, エラーメッセージ)
        """
```

### 5. ClipboardService (services/clipboard_service.py)

クリップボード操作を担当するサービスクラス。

```python
class ClipboardService:
    """クリップボード操作サービス (SRP)"""

    def __init__(self, executor: X11CommandExecutor):
        """
        Args:
            executor: コマンド実行ユーティリティ
        """

    def copy_to_clipboard(self, text: str) -> tuple[bool, str]:
        """
        クリップボードにテキストをコピー

        Args:
            text: コピーするテキスト

        Returns:
            tuple[bool, str]: (成功したか, エラーメッセージ)
        """

    def get_from_clipboard(self) -> tuple[bool, str, str]:
        """
        クリップボードからテキストを取得

        Returns:
            tuple[bool, str, str]: (成功したか, テキスト, エラーメッセージ)
        """
```

### 6. TextService (services/text_service.py)

テキスト送受信の統合サービスクラス。WindowServiceとClipboardServiceを組み合わせて使用。

```python
class TextService:
    """テキスト送受信の統合サービス (SRP, DIP)"""

    def __init__(self,
                 window_service: WindowService,
                 clipboard_service: ClipboardService,
                 executor: X11CommandExecutor):
        """
        Args:
            window_service: ウィンドウ操作サービス
            clipboard_service: クリップボード操作サービス
            executor: コマンド実行ユーティリティ
        """

    def send_text(self, window_id: str, text: str,
                  activate_wait: float, key_wait: float) -> tuple[bool, str]:
        """
        テキストを指定ウィンドウに送信

        処理フロー:
        1. クリップボードにテキストをコピー
        2. ウィンドウをアクティブ化
        3. activate_wait秒待機
        4. Ctrl+Vでペースト

        Args:
            window_id: 送信先ウィンドウのID
            text: 送信するテキスト
            activate_wait: ウィンドウアクティブ化後の待機時間
            key_wait: キー入力後の待機時間(現在未使用)

        Returns:
            tuple[bool, str]: (成功したか, エラーメッセージ)
        """

    def receive_text(self, key_wait: float) -> tuple[bool, str, str]:
        """
        アクティブウィンドウからテキストを取得

        処理フロー:
        1. Ctrl+A (全選択)
        2. key_wait秒待機
        3. Ctrl+C (コピー)
        4. key_wait秒待機
        5. クリップボードから取得

        Args:
            key_wait: キー入力間の待機時間

        Returns:
            tuple[bool, str, str]: (成功したか, テキスト, エラーメッセージ)
        """
```

### 7. MainWindow (ui/main_window.py)

メインウィンドウのUIクラス。Qt Designerで作成した`.ui`ファイルをロード。

```python
class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(self,
                 text_service: TextService,
                 window_service: WindowService,
                 config_manager: ConfigManager):
        """
        Args:
            text_service: テキスト送受信サービス
            window_service: ウィンドウ操作サービス
            config_manager: 設定管理
        """

    # UI要素 (.uiファイルから読み込み)
    # - window_list: QListWidget          # ウィンドウ一覧
    # - text_edit: QPlainTextEdit         # 複数行テキストボックス
    # - send_button: QPushButton          # 送信ボタン
    # - copy_button: QPushButton          # コピーボタン
    # - refresh_button: QPushButton       # リフレッシュボタン
    # - status_label: QLabel              # ステータス表示
    # - menu_bar: QMenuBar                # 設定メニュー

    def setup_ui(self) -> None:
        """
        UIをセットアップ
        - .uiファイルをロード (uic.loadUi())
        - シグナルとスロットを接続
        - 常に最前面フラグを設定
        """

    def refresh_window_list(self) -> None:
        """ウィンドウ一覧を更新"""

    def on_send_clicked(self) -> None:
        """送信ボタンクリック時の処理"""

    def on_copy_clicked(self) -> None:
        """コピーボタンクリック時の処理"""

    def on_settings_clicked(self) -> None:
        """設定メニュークリック時の処理"""

    def show_status(self, message: str, is_error: bool = False) -> None:
        """ステータスバーにメッセージを表示"""

    def closeEvent(self, event) -> None:
        """ウィンドウクローズ時にウィンドウサイズを保存"""
```

### 8. SettingsDialog (ui/settings_dialog.py)

設定ダイアログのUIクラス。Qt Designerで作成した`.ui`ファイルをロード。

```python
class SettingsDialog(QDialog):
    """設定ダイアログ"""

    def __init__(self, config_manager: ConfigManager):
        """
        Args:
            config_manager: 設定管理
        """

    # UI要素 (.uiファイルから読み込み)
    # - window_activate_wait_input: QDoubleSpinBox
    # - key_input_wait_input: QDoubleSpinBox
    # - copyfrom_wait_input: QDoubleSpinBox
    # - save_button: QPushButton
    # - cancel_button: QPushButton

    def setup_ui(self) -> None:
        """
        UIをセットアップ
        - .uiファイルをロード (uic.loadUi())
        - シグナルとスロットを接続
        """

    def load_settings(self) -> None:
        """現在の設定値をUIに反映"""

    def save_settings(self) -> None:
        """UIの値を設定として保存"""
```

## 処理フロー

### 起動時

1. `DependencyChecker.check_dependencies()`実行
2. xdotool/xclipが不足している場合
   - エラーダイアログ表示: 「以下のツールがインストールされていません: [ツール名]」
   - アプリケーション終了
3. `ConfigManager`で設定ファイル読み込み(なければデフォルト値使用)
4. 各Serviceクラスのインスタンス生成
5. `MainWindow`表示(常に最前面フラグ設定)
6. 自動的にウィンドウ一覧を取得・表示

### テキスト送信(typeinto)

1. ウィンドウリストから選択されているか確認
   - 未選択: ステータスバーに「ウィンドウを選択してください」と表示
2. テキストボックスが空でないか確認
   - 空: ステータスバーに「送信するテキストを入力してください」と表示
3. `TextService.send_text()`呼び出し
   - `ClipboardService.copy_to_clipboard(text)`
   - `WindowService.activate_window(window_id, wait_time)`
   - `sleep(window_activate_wait)`
   - `xdotool key ctrl+v` 実行
4. 成功: ステータスバーに「テキストを送信しました」
5. 失敗: ステータスバーに赤文字で「エラー: [エラーメッセージ]」

### テキストコピー(copyfrom)

1. ステータスバーに「{copyfrom_wait}秒後にコピーを開始します。対象のテキストボックスをクリックしてください」と表示
2. `sleep(copyfrom_wait)`
3. `TextService.receive_text()`呼び出し
   - `xdotool key ctrl+a` 実行
   - `sleep(key_input_wait)`
   - `xdotool key ctrl+c` 実行
   - `sleep(key_input_wait)`
   - `ClipboardService.get_from_clipboard()`
4. 成功: 取得したテキストをテキストボックスに表示、ステータスバーに「テキストをコピーしました」
5. 失敗: ステータスバーに赤文字で「エラー: [エラーメッセージ]」

### リフレッシュ

1. `WindowService.get_window_list()`呼び出し
2. `QListWidget`のアイテムをクリア
3. 新しいウィンドウリストで更新
4. ステータスバーに「ウィンドウリストを更新しました」と表示

### 設定

1. メニューから「設定」選択
2. `SettingsDialog`をモーダル表示
3. 現在の設定値をUIに表示
4. ユーザーが値を変更
5. 保存ボタンクリック
   - `ConfigManager.set_timing()`で各値を設定
   - `ConfigManager.save_config()`で設定ファイルに書き込み
   - ダイアログを閉じる
6. キャンセルボタンクリック
   - 変更を破棄してダイアログを閉じる

## エラーハンドリング

### 起動時エラー

- **xdotool/xclip未インストール**:
  - QMessageBox.critical()でエラーダイアログ表示
  - 「以下のツールがインストールされていません:\n- xdotool\n- xclip\n\nsudo apt install xdotool xclip でインストールしてください」
  - アプリケーション終了(sys.exit(1))

### 実行時エラー

- **ウィンドウが見つからない**:
  - ステータスバーに赤文字で「エラー: ウィンドウが見つかりません」

- **クリップボード操作失敗**:
  - ステータスバーに赤文字で「エラー: クリップボード操作に失敗しました」

- **コマンド実行失敗**:
  - ステータスバーに赤文字で「エラー: [stderr内容]」

- **設定ファイル読み込み失敗**:
  - デフォルト値を使用
  - ログに警告出力(将来的に)

## 実装計画

### Phase 1: 基盤構築 ✓ 完了
**目的**: プロジェクト構造とユーティリティの実装

1. プロジェクト構造の作成
   - ディレクトリ構造作成
   - `__init__.py`ファイル配置
   - `requirements.txt`作成 (PyQt6含む)
   - `.gitignore`, `README.md`, `LICENSE.txt`作成

2. ユーティリティクラスの実装
   - `X11CommandExecutor`実装
   - `DependencyChecker`実装
   - unittestベースのテスト作成

3. 設定管理の実装
   - `ConfigManager`実装 (JSON形式、`$HOME/.config/mini-text/`に保存)
   - デフォルト値設定
   - ディレクトリ自動作成機能
   - 読み書きテスト

**成果物**:
- 基本プロジェクト構造
- ユーティリティクラス (X11CommandExecutor, DependencyChecker)
- 設定管理機能 (ConfigManager)
- 14個のユニットテスト

**検証結果**:
- ✓ 全14テストが成功
- ✓ `DependencyChecker`で依存関係確認が動作
- ✓ `ConfigManager`で設定ファイルの読み書きが動作
- ✓ 設定ファイルディレクトリが自動作成される

---

### Phase 2: サービスレイヤー実装 ✓ 完了
**目的**: ビジネスロジックの実装

1. `WindowService`実装
   - ウィンドウ一覧取得 (`get_window_list()`)
   - ウィンドウアクティベート (`activate_window()`)
   - unittestテスト作成

2. `ClipboardService`実装
   - クリップボードへの書き込み (`copy_to_clipboard()`)
   - クリップボードからの読み込み (`get_from_clipboard()`)
   - unittestテスト作成

3. `TextService`実装
   - `send_text()`実装 (統合処理)
   - `receive_text()`実装 (統合処理)
   - unittestテスト作成

**成果物**:
- 全サービスクラス (WindowService, ClipboardService, TextService)
- 18個のユニットテスト (合計32テスト)

**検証結果**:
- ✓ 全32テストが成功 (Phase 1: 14 + Phase 2: 18)
- ✓ WindowService: ウィンドウ一覧取得とアクティベートが動作
- ✓ ClipboardService: クリップボード操作が動作
- ✓ TextService: テキスト送受信の統合処理が動作
- ✓ SOLID原則(SRP, DIP)に準拠した設計

---

### Phase 3: 基本UI実装
**目的**: 最小限のGUIで動作確認

**前提条件**: Qt6 Designerのインストールが必要
```bash
# Ubuntu/Debianの場合
sudo apt install qt6-tools-dev qt6-tools-dev-tools

# インストール確認
which designer-qt6
```

**UIファイル作成オプション**:

**オプション1: Qt Designerを使用 (推奨)**
1. Qt Designer (designer-qt6)を起動
2. Main Window テンプレートを選択
3. GUI上でウィジェットを配置:
   - ウィンドウ一覧 (QListWidget) - オブジェクト名: `window_list`
   - テキストボックス (QPlainTextEdit) - オブジェクト名: `text_edit`
   - 送信ボタン (QPushButton) - オブジェクト名: `send_button`
   - コピーボタン (QPushButton) - オブジェクト名: `copy_button`
   - リフレッシュボタン (QPushButton) - オブジェクト名: `refresh_button`
   - ステータスバー (QStatusBar) - オブジェクト名: `statusBar`
4. `mini_text/ui/resources/main_window.ui`として保存

**オプション2: .uiファイルを直接作成**
- XMLフォーマットで`.ui`ファイルを直接記述
- Claude Codeが.uiファイルのXMLを生成可能
- Qt Designerがない環境でも実装を進められる
- 後でQt Designerで微調整可能

**実装手順**:

1. UIファイルの準備 (上記オプションのいずれかで作成)
   - `mini_text/ui/resources/main_window.ui`

2. `MainWindow`の実装
   - `.ui`ファイルをロード (`uic.loadUi()`)
   - シグナルとスロットを接続
   - 常に最前面フラグを設定
   - イベントハンドラ実装

3. `main.py`実装
   - 起動時の依存関係チェック
   - サービスインスタンス生成
   - MainWindow表示

**成果物**:
- 動作する基本的なGUIアプリケーション
- Qt Designer UIファイル (または直接作成した.uiファイル)

**検証**:
- アプリケーションが起動するか
- ウィンドウリストが表示されるか
- テキスト送信が動作するか
- テキストコピーが動作するか
- (Qt Designerがあれば) UIを開いて編集できるか

---

### Phase 4: 設定機能実装
**目的**: 設定UIとウィンドウサイズ保存

1. Qt Designer で設定ダイアログUIファイル作成
   - `mini_text/ui/resources/settings_dialog.ui`作成
   - タイミング設定の入力フィールド (QDoubleSpinBox)
   - 保存/キャンセルボタン

2. `SettingsDialog`実装
   - `.ui`ファイルをロード
   - シグナルとスロットを接続
   - 設定の読み込み・保存処理

3. メニューバー実装 (main_window.uiで追加)
   - ファイルメニュー
   - 設定メニュー項目
   - 終了メニュー項目

4. ウィンドウサイズ保存
   - `closeEvent()`でサイズ保存
   - 起動時にサイズ復元

**成果物**:
- 完全な設定機能
- ウィンドウサイズの永続化
- 設定ダイアログUIファイル

**検証**:
- 設定ダイアログが開くか
- 設定値の変更が保存されるか
- ウィンドウサイズが保存・復元されるか
- Qt Designerで設定ダイアログUIを編集できるか

---

### Phase 5: 改善・テスト
**目的**: UX改善とバグ修正

1. エラーハンドリング強化
   - 各エラーケースの確認
   - エラーメッセージの改善

2. UI/UX改善
   - ボタンの有効/無効制御
   - キーボードショートカット(オプション)
   - ツールチップ追加

3. ドキュメント作成
   - `README.md`作成
   - 使用方法の説明
   - スクリーンショット追加(オプション)

4. 統合テスト
   - 様々なアプリケーションでテスト
   - 日本語テキストのテスト
   - 複数行テキストのテスト

**成果物**:
- 本番利用可能なアプリケーション
- ドキュメント

**検証**:
- 実際の使用シナリオで問題なく動作するか
- エラーが適切にハンドリングされるか

---

### 各フェーズの所要時間見積もり

- **Phase 1**: 1-2時間
- **Phase 2**: 2-3時間
- **Phase 3**: 3-5時間 (Qt Designer作業含む)
- **Phase 4**: 2-4時間 (Qt Designer作業含む)
- **Phase 5**: 2-3時間

**合計**: 10-17時間程度

### 実装の進め方

1. 各フェーズ完了時に動作確認を行う
2. 問題があれば次フェーズに進む前に修正
3. 各フェーズで必要に応じて設計を見直し、このドキュメントを更新
4. コミットは機能単位で細かく行う(フェーズ単位ではなく)

## Qt Designer使用に関する注意事項

### UIファイルの読み込み方法

以下の2つの方法がありますが、本プロジェクトでは**方法2 (ランタイムロード)** を採用します。

**方法1: pyuic6でPythonコードに変換**
```bash
pyuic6 -o ui_main_window.py main_window.ui
```
- メリット: 実行時の依存が少ない
- デメリット: UIを変更するたびに再変換が必要

**方法2: ランタイムで.uiファイルをロード (採用)**
```python
from PyQt6 import uic
uic.loadUi('mini_text/ui/resources/main_window.ui', self)
```
- メリット: .uiファイルの変更がすぐに反映される、開発が高速
- デメリット: 実行時に.uiファイルが必要

### UIファイルでの命名規則

UIエレメントのオブジェクト名は以下の規則に従います:

- `window_list`: ウィンドウ一覧 (QListWidget)
- `text_edit`: テキスト入力/表示 (QPlainTextEdit)
- `send_button`: 送信ボタン (QPushButton)
- `copy_button`: コピーボタン (QPushButton)
- `refresh_button`: リフレッシュボタン (QPushButton)
- `status_label`: ステータスラベル (QLabel) ※ステータスバーはQStatusBarを使用することも検討

## 今後の拡張案

- Waylandサポート
- ウィンドウフィルタリング機能
- テキスト送信履歴
- プリセット機能(よく使うテキストの保存)
- ホットキーサポート
- 複数ウィンドウへの一括送信
