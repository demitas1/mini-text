# mini-text プロジェクト状況サマリー

**最終更新**: 2025-11-02

## プロジェクト概要

Linux X11デスクトップ環境で、ウィンドウ間のテキスト送受信を支援するPyQt6アプリケーション。

## 実装進捗

| Phase | 内容 | 状態 | 完了日 |
|-------|------|------|--------|
| Phase 1 | 基盤構築 | ✓ 完了 | 2025-11-02 |
| Phase 2 | サービスレイヤー実装 | ✓ 完了 | 2025-11-02 |
| Phase 3 | 基本UI実装 | ✓ 完了 | 2025-11-02 |
| Phase 4 | 設定機能実装 | 未着手 | - |
| Phase 5 | 改善・テスト | 未着手 | - |

## Phase 1: 基盤構築 ✓

### 実装内容
- プロジェクト構造作成
- `X11CommandExecutor`: xdotool/xclip実行
- `DependencyChecker`: 依存関係チェック
- `ConfigManager`: JSON設定管理（`$HOME/.config/mini-text/config.json`）
- unittestベースのテスト構造

### 成果物
- 14個のユニットテスト（全て成功）
- `.gitignore`, `README.md`, `LICENSE.txt`

## Phase 2: サービスレイヤー実装 ✓

### 実装内容
- `WindowService`: ウィンドウ一覧取得・アクティベート
- `ClipboardService`: クリップボード操作
- `TextService`: テキスト送受信統合（SRP/DIP原則に準拠）

### 成果物
- 18個のユニットテスト（合計32テスト、全て成功）
- SOLID原則に準拠した設計

## Phase 3: 基本UI実装 ✓

### 実装内容
- `main_window.ui`: Qt Designer形式のUIファイル（XML直接作成）
- `MainWindow`: PyQt6メインウィンドウ（uic.loadUi()）
- `main.py`: エントリーポイント、依存関係チェック
- fcitx5統合対応（環境変数設定、プラグインパス設定）

### 動作確認済み機能
- ✓ アプリケーション起動
- ✓ ウィンドウ一覧表示・リフレッシュ
- ✓ 常に最前面表示
- ✓ テキスト送信（英数字）
- ✓ テキストコピー
- ✓ ウィンドウサイズ保存・復元
- ✓ エラーハンドリング
- ✓ メニュー（設定は未実装）

### 既知の問題
- ✗ **IME（日本語入力）が動作しない**
  - 原因: venv内PyQt6とシステムfcitx5プラグインのQt6バージョン不一致
  - 詳細: `docs/design/ime-integration-issue.md`
  - 影響: 日本語入力不可、英数字のみ使用可能

## テスト結果

```
総テスト数: 32
成功: 32
失敗: 0
成功率: 100%
```

### テスト内訳
- Phase 1ユーティリティ: 14テスト
- Phase 2サービス: 18テスト
- Phase 3 UI: 手動確認

## 現在の課題

### 1. IME統合問題（高優先度）

**問題**: fcitx5/mozcによる日本語入力ができない

**原因**:
- venv環境のPyQt6 (6.10.0) とシステムQt6プラグインのABI不一致
- Qt6プライベートAPIの互換性なし

**解決策の選択肢**:
1. システムPyQt6を使用（`--system-site-packages`）
2. PySide6に移行（要検証）
3. Tkinterに移行（大規模書き換え）
4. GTK4に移行（大規模書き換え）

**推奨**: まず選択肢1でPhase 4-5を完了し、後で選択肢2を検証

## 次のステップ

### 短期（Phase 4-5完了）
1. IME問題の暫定対応検討
2. Phase 4: 設定ダイアログ実装
3. Phase 5: UI/UX改善、統合テスト、ドキュメント整備

### 中長期（リファクタリング）
1. PySide6での動作検証
2. 必要に応じてUIツールキットの移行検討
3. 追加機能の実装（拡張案参照）

## ファイル構成

```
mini-text/
├── main.py                    # エントリーポイント
├── requirements.txt           # PyQt6 6.6.0+
├── README.md                  # プロジェクト概要
├── LICENSE.txt                # MIT License
├── STATUS.md                  # このファイル
├── TESTING.md                 # Phase 3動作確認手順
├── mini_text/                 # メインパッケージ
│   ├── config/                # 設定管理
│   ├── utils/                 # ユーティリティ
│   ├── services/              # サービスレイヤー
│   └── ui/                    # UIレイヤー
│       └── resources/
│           └── main_window.ui
├── tests/                     # ユニットテスト
│   └── *.py (32テスト)
└── docs/
    ├── design/
    │   ├── application-idea.md
    │   ├── detailed-design.md
    │   └── ime-integration-issue.md
    └── examples/

26ファイル、32ユニットテスト
```

## 開発メモ

### 学んだこと
1. venv環境でのGUIアプリケーション開発の課題
   - システム統合（IME、テーマ）がvenvの隔離性と衝突
   - C++バインディング（PyQt6）はシステムライブラリとの互換性が重要

2. 早期の環境検証の重要性
   - IME統合のような重要機能は設計初期段階で検証すべき
   - プロトタイプでの動作確認が不可欠

3. SOLID原則の有効性
   - サービスレイヤーの分離により、テストが容易
   - 将来的なUIツールキット変更時、ビジネスロジックは再利用可能

### 技術スタック
- Python 3.12
- PyQt6 6.10.0
- xdotool, xclip
- unittest
- JSON設定管理

### 開発環境
- Ubuntu 24.04.3 LTS
- KDE (X11)
- fcitx5 5.1.7 + mozc
- venv仮想環境

## 参考リンク

- [SOLID原則](https://en.wikipedia.org/wiki/SOLID)
- [PyQt6ドキュメント](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [fcitx5](https://github.com/fcitx/fcitx5)
