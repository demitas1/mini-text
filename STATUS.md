# mini-text プロジェクト状況サマリー

**最終更新**: 2025-11-03

## プロジェクト概要

Linux X11デスクトップ環境で、ウィンドウ間のテキスト送受信を支援するデスクトップアプリケーション。

## 実装バリエーション

### PyQt6実装 (`pyqt/`)

**ステータス**: Phase 3完了、IME問題により中断

- **長所**: pip完結、Qt Designerによる視覚的UI設計
- **短所**: IME（日本語入力）が動作しない
- **詳細**: `docs/design/pyqt/ime-integration-issue.md`参照

### GTK4実装 (`gtk4/`) ⭐ 推奨

**ステータス**: Phase 3完了、動作確認済み ✓

- **長所**: IME統合が正常動作、日本語入力対応
- **短所**: システムPyGObjectに依存
- **詳細**: `docs/design/gtk4-detailed-design.md`参照

## GTK4実装進捗

| Phase | 内容 | 状態 | 完了日 |
|-------|------|------|--------|
| Phase 1 | 基盤構築 | ✓ 完了 | 2025-11-03 |
| Phase 2 | サービスレイヤー実装 | ✓ 完了 | 2025-11-03 |
| Phase 3 | 基本UI実装 | ✓ 完了 | 2025-11-03 |
| Phase 4 | 設定機能実装 | 未着手 | - |
| Phase 5 | 改善・テスト | 未着手 | - |

## Phase 1: 基盤構築 ✓

### 実装内容
- プロジェクト構造作成
- PyQt6からの共通レイヤーコピー（独立ファイル）
  - `ConfigManager`: JSON設定管理
  - `X11CommandExecutor`: xdotool/xclip実行
  - `DependencyChecker`: 依存関係チェック
- pytest環境構築
- venv作成（`--system-site-packages`）

### 成果物
- 14個のpytestテスト（全て成功）
- requirements.txt（システムPyGObject使用）
- conftest.py（フィクスチャ定義）

## Phase 2: サービスレイヤー実装 ✓

### 実装内容
- PyQt6からサービスクラスをコピー
  - `WindowService`: ウィンドウ一覧取得・アクティベート
  - `ClipboardService`: クリップボード操作
  - `TextService`: テキスト送受信統合
- unittestからpytest形式にテスト変換
- ConfigManagerのバグ修正（浅いコピー問題）

### 成果物
- 18個のpytestテスト（合計32テスト、全て成功）
- SOLID原則に準拠した設計（PyQt6から継承）

## Phase 3: 基本UI実装 ✓

### 実装内容
- Glade形式のUIファイル作成（`main_window.ui`）
- GTK4 MainWindowクラス実装
  - Gtk.Template使用
  - シグナル接続
  - 常に最前面表示
- main.pyエントリーポイント作成
  - Gtk.Applicationベース
  - 依存関係チェック統合
  - アクション設定（設定、終了）

### 実装済み機能
- ✓ アプリケーション起動
- ✓ ウィンドウ一覧表示・リフレッシュ
- ✓ テキスト送信機能
- ✓ テキストコピー機能
- ✓ 常に最前面表示（GTK4の制限あり）
- ✓ ウィンドウサイズ保存・復元
- ✓ エラーハンドリング
- ✓ ステータスバー表示
- ✓ メニュー（設定は未実装）

### 動作確認済み ✓
- ✓ 実際のGUI起動テスト
- ✓ **IME/日本語入力テスト（成功！）**
- ✓ ウィンドウ間テキスト送受信テスト（Inkscapeで確認）
- ✓ エラーケーステスト

## テスト結果

```
総テスト数: 32
成功: 32
失敗: 0
成功率: 100%
```

### テスト内訳
- ConfigManager: 7テスト
- DependencyChecker: 2テスト
- X11CommandExecutor: 5テスト
- WindowService: 5テスト
- ClipboardService: 5テスト
- TextService: 8テスト

## Phase 3で解決した問題

### クリップボードコピーのタイムアウト問題
**問題**: `xclip`コマンドがクリップボードにテキストをコピーする際にタイムアウトが発生

**原因**: xclipはクリップボード所有権を保持し続けるためプロセスが終了せず、`subprocess.run()`が待機し続ける

**解決策**:
1. `subprocess.Popen()`を使用してバックグラウンドで起動
2. `start_new_session=True`で別セッションとして起動
3. `communicate(timeout=0.5)`でデータを渡し、タイムアウトを正常と判断
4. `-i`フラグを追加して明示的に入力モードを指定

**影響ファイル**:
- `gtk4/mini_text/utils/x11_command_executor.py:25-61`
- `gtk4/mini_text/services/clipboard_service.py:27-30`
- `gtk4/tests/test_clipboard_service.py:32-33, 91-93`

## 次のステップ

### 短期（Phase 4）
1. Phase 4: 設定ダイアログ実装
   - タイミング設定のGUI
   - 設定の保存・読み込み

### 中期（Phase 5）
1. Phase 5: UI/UX改善、統合テスト、ドキュメント整備
   - キーボードショートカット
   - ウィンドウ検索機能
   - エラーメッセージの改善

### 長期（オプション）
1. 追加機能の実装
2. パッケージング（.deb等）
3. リリース準備

## ファイル構成

```
mini-text/
├── gtk4/                      # GTK4実装（推奨）
│   ├── main.py                # エントリーポイント
│   ├── requirements.txt       # pytest, pytest-cov
│   ├── README.md              # GTK4実装ドキュメント
│   ├── TESTING.md             # 動作確認手順
│   ├── mini_text/
│   │   ├── config/            # 設定管理
│   │   ├── utils/             # ユーティリティ
│   │   ├── services/          # サービスレイヤー
│   │   └── ui/                # UIレイヤー
│   │       ├── main_window.py
│   │       └── resources/
│   │           └── main_window.ui
│   └── tests/                 # pytest (32テスト)
├── pyqt/                      # PyQt6実装（IME問題により中断）
│   └── ...
├── docs/
│   ├── design/
│   │   ├── application-idea.md       # 共通アイディア
│   │   ├── gtk4-detailed-design.md   # GTK4設計書
│   │   └── pyqt/                     # PyQt6関連ドキュメント
│   └── examples/
│       ├── typeinto.sh
│       └── copyfrom.sh
├── README.md                  # プロジェクト概要
├── STATUS.md                  # このファイル
├── CLAUDE.md                  # 開発ガイドライン
└── LICENSE.txt
```

## 技術スタック

### GTK4実装
- Python 3.12
- GTK 4.0
- PyGObject 3.48.2（システムパッケージ）
- pytest 8.4.2
- xdotool, xclip

### 開発環境
- Ubuntu 24.04.3 LTS
- KDE (X11)
- fcitx5 5.1.7 + mozc
- venv（--system-site-packages）

## 学んだこと

### PyQt6実装での課題
1. venv環境でのIME統合問題
   - venv内PyQt6とシステムfcitx5プラグインのバージョン不一致
   - Qt6プライベートAPIの互換性なし

2. 解決策の模索
   - システムPyQt6使用（`--system-site-packages`）
   - 他のUIツールキット検討 → GTK4採用

### GTK4実装での成功
1. システムPyGObject使用
   - `--system-site-packages`で問題解決
   - fcitx5/mozcとの統合が安定

2. SOLID原則の有効性
   - サービスレイヤーの分離により、UIツールキット変更が容易
   - PyQt6からGTK4への移行がスムーズ

3. pytest採用
   - unittestより簡潔で読みやすい
   - フィクスチャの再利用が容易

4. xclipの仕様理解
   - クリップボード所有権保持のためプロセスが終了しない仕様
   - `subprocess.Popen()`でバックグラウンド実行することで解決
   - X11のクリップボードメカニズムの理解が深まった

## 参考リンク

- [GTK4ドキュメント](https://docs.gtk.org/gtk4/)
- [PyGObjectドキュメント](https://pygobject.readthedocs.io/)
- [Gladeドキュメント](https://glade.gnome.org/)
- [SOLID原則](https://en.wikipedia.org/wiki/SOLID)
