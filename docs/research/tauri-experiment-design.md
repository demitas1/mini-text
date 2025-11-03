# Tauri実験プロジェクト設計書

**作成日**: 2025-11-03
**目的**: IMEとクリップボード動作の検証
**プロジェクトパス**: `tauri/experiment/`

## 1. プロジェクト概要

### 目的
GTK4実装からTauri移植の前に、以下の重要な懸念事項を検証する:
1. **IME/日本語入力**: WebViewベースのUIで日本語入力（fcitx5/mozc）が正しく動作するか
2. **クリップボード操作**: Tauri公式Clipboard Pluginが期待通りに動作するか

### スコープ
最小限の機能のみを実装:
- シンプルなGUIウィンドウ
- 複数行テキストボックス（日本語入力テスト用）
- クリップボードへの書き込みボタン
- クリップボードからの読み込みボタン
- 外部ファイルでUI設計を管理

### 成功基準
- ✅ 日本語入力（ひらがな、漢字変換）が正常に動作
- ✅ クリップボードへのコピーが成功
- ✅ クリップボードからのペーストが成功
- ✅ 複数行テキストが正しく扱える
- ✅ UIがHTMLファイルから読み込まれる

## 2. プロジェクト構成

```
tauri/experiment/
├── src/                        # Rustバックエンド
│   └── main.rs                 # エントリーポイント
├── src-tauri/                  # Tauri設定
│   ├── Cargo.toml              # Rust依存関係
│   ├── tauri.conf.json         # Tauri設定ファイル
│   ├── build.rs                # ビルドスクリプト
│   ├── src/
│   │   ├── main.rs             # Rustメインコード
│   │   └── lib.rs              # ライブラリ定義（必要に応じて）
│   └── capabilities/           # セキュリティ設定
│       └── default.json
├── ui/                         # フロントエンド（外部編集可能）
│   ├── index.html              # メインUI（人間が編集）
│   ├── styles.css              # スタイル（人間が編集）
│   └── script.js               # UIロジック（人間が編集）
├── package.json                # npm設定（Tauri CLI用）
└── README.md                   # プロジェクト説明
```

## 3. UI設計

### 3.1 画面レイアウト

```
┌─────────────────────────────────────────┐
│  Tauri Clipboard & IME Test            │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │  複数行テキストボックス              │  │
│  │  （日本語入力可能）                  │  │
│  │                                   │  │
│  │  ここに文字を入力...                │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌─────────┐  ┌─────────┐              │
│  │ 送信    │  │ コピー   │              │
│  └─────────┘  └─────────┘              │
│                                         │
│  ステータス: [操作結果を表示]            │
│                                         │
└─────────────────────────────────────────┘
```

### 3.2 HTMLファイル構成 (`ui/index.html`)

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tauri Clipboard & IME Test</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Tauri Clipboard & IME Test</h1>

        <div class="text-area-container">
            <textarea
                id="mainTextArea"
                placeholder="ここに文字を入力してください...&#x0A;日本語入力（ひらがな、漢字）をテストできます。"
                rows="10"
            ></textarea>
        </div>

        <div class="button-container">
            <button id="sendButton" class="btn btn-primary">送信（クリップボードへコピー）</button>
            <button id="copyButton" class="btn btn-secondary">コピー（クリップボードから貼り付け）</button>
        </div>

        <div class="status-container">
            <p id="statusMessage">ステータス: 待機中</p>
        </div>
    </div>

    <script type="module" src="script.js"></script>
</body>
</html>
```

### 3.3 CSSファイル構成 (`ui/styles.css`)

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, "Noto Sans", sans-serif,
                 "Noto Sans JP", "Hiragino Kaku Gothic ProN", Meiryo;
    background-color: #f5f5f5;
    padding: 20px;
}

.container {
    max-width: 600px;
    margin: 0 auto;
    background-color: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h1 {
    font-size: 24px;
    margin-bottom: 20px;
    color: #333;
}

.text-area-container {
    margin-bottom: 20px;
}

#mainTextArea {
    width: 100%;
    padding: 12px;
    font-size: 14px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: vertical;
    font-family: inherit;
    line-height: 1.5;
}

#mainTextArea:focus {
    outline: none;
    border-color: #4CAF50;
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.button-container {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.btn {
    padding: 10px 20px;
    font-size: 14px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.btn-primary {
    background-color: #4CAF50;
    color: white;
}

.btn-primary:hover {
    background-color: #45a049;
}

.btn-secondary {
    background-color: #2196F3;
    color: white;
}

.btn-secondary:hover {
    background-color: #0b7dda;
}

.status-container {
    padding: 12px;
    background-color: #f9f9f9;
    border-radius: 4px;
    border-left: 4px solid #4CAF50;
}

#statusMessage {
    font-size: 14px;
    color: #666;
}

.status-error {
    border-left-color: #f44336 !important;
}

.status-error #statusMessage {
    color: #f44336;
}

.status-success {
    border-left-color: #4CAF50 !important;
}

.status-success #statusMessage {
    color: #4CAF50;
}
```

### 3.4 JavaScriptファイル構成 (`ui/script.js`)

```javascript
// Tauri APIのインポート
import { writeText, readText } from '@tauri-apps/plugin-clipboard-manager';

// DOM要素の取得
const textArea = document.getElementById('mainTextArea');
const sendButton = document.getElementById('sendButton');
const copyButton = document.getElementById('copyButton');
const statusMessage = document.getElementById('statusMessage');
const statusContainer = document.querySelector('.status-container');

// ステータス更新ヘルパー関数
function updateStatus(message, type = 'info') {
    statusMessage.textContent = `ステータス: ${message}`;
    statusContainer.classList.remove('status-error', 'status-success');

    if (type === 'error') {
        statusContainer.classList.add('status-error');
    } else if (type === 'success') {
        statusContainer.classList.add('status-success');
    }
}

// 送信ボタン: テキストボックスの内容をクリップボードにコピー
sendButton.addEventListener('click', async () => {
    try {
        const text = textArea.value;

        if (!text.trim()) {
            updateStatus('テキストが空です', 'error');
            return;
        }

        await writeText(text);
        updateStatus(`クリップボードにコピーしました (${text.length}文字)`, 'success');

    } catch (error) {
        console.error('クリップボードへのコピーエラー:', error);
        updateStatus(`エラー: ${error.message}`, 'error');
    }
});

// コピーボタン: クリップボードの内容をテキストボックスにペースト
copyButton.addEventListener('click', async () => {
    try {
        const clipboardText = await readText();

        if (clipboardText === null || clipboardText === undefined) {
            updateStatus('クリップボードにテキストがありません', 'error');
            return;
        }

        textArea.value = clipboardText;
        updateStatus(`クリップボードから貼り付けました (${clipboardText.length}文字)`, 'success');

    } catch (error) {
        console.error('クリップボードからの読み取りエラー:', error);
        updateStatus(`エラー: ${error.message}`, 'error');
    }
});

// 初期化
updateStatus('待機中');
```

## 4. Rust実装設計

### 4.1 Cargo.toml依存関係

```toml
[package]
name = "tauri-clipboard-test"
version = "0.1.0"
edition = "2021"

[build-dependencies]
tauri-build = { version = "2", features = [] }

[dependencies]
tauri = { version = "2", features = ["devtools"] }
tauri-plugin-clipboard-manager = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"

[features]
default = ["custom-protocol"]
custom-protocol = ["tauri/custom-protocol"]
```

### 4.2 main.rs実装

```rust
// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        // Clipboard Managerプラグインを初期化
        .plugin(tauri_plugin_clipboard_manager::init())
        // アプリケーションを実行
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**実装のポイント**:
- 最小限の実装（Commandは不要、JavaScript側で直接プラグインAPI使用）
- Clipboard Managerプラグインの初期化のみ

### 4.3 tauri.conf.json設定

```json
{
  "productName": "tauri-clipboard-test",
  "version": "0.1.0",
  "identifier": "com.minitext.clipboard-test",
  "build": {
    "frontendDist": "../ui"
  },
  "app": {
    "windows": [
      {
        "title": "Tauri Clipboard & IME Test",
        "width": 700,
        "height": 600,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ]
  }
}
```

**設定のポイント**:
- `frontendDist`: UIファイルの場所を`../ui`に指定（外部編集可能）
- `windows`: ウィンドウサイズは700x600で開始
- `security.csp`: 開発中はnullで制限を緩和

### 4.4 Capabilities設定 (`src-tauri/capabilities/default.json`)

```json
{
  "$schema": "https://tauri.app/schema/capability.json",
  "identifier": "default",
  "description": "Default capability for clipboard operations",
  "windows": ["main"],
  "permissions": [
    "clipboard-manager:allow-read-text",
    "clipboard-manager:allow-write-text"
  ]
}
```

**セキュリティのポイント**:
- クリップボード読み取り・書き込み権限のみ許可
- 最小権限原則に基づく

## 5. 実装手順

### Phase 1: プロジェクト初期化

```bash
# 作業ディレクトリに移動
cd /mnt/ext-ssd1/work/github.com/mini-text

# Tauriプロジェクト作成
npm create tauri-app@latest -- \
  --template vanilla \
  --manager npm \
  tauri/experiment

# プロジェクトディレクトリに移動
cd tauri/experiment
```

### Phase 2: プロジェクト構造の調整

```bash
# UIディレクトリを作成（外部編集用）
mkdir ui

# テンプレートのindex.htmlを移動（あれば）
mv index.html ui/
mv styles.css ui/ 2>/dev/null || true
mv main.js ui/script.js 2>/dev/null || true

# src-tauriに移動
cd src-tauri
```

### Phase 3: 依存関係のインストール

**Cargo.toml編集**:
```bash
# clipboard-managerプラグインを追加
cargo add tauri-plugin-clipboard-manager
```

**package.json編集**:
```bash
cd ..
npm install @tauri-apps/plugin-clipboard-manager
```

### Phase 4: ファイル作成

1. `ui/index.html` を上記設計に従って作成
2. `ui/styles.css` を上記設計に従って作成
3. `ui/script.js` を上記設計に従って作成
4. `src-tauri/src/main.rs` を上記設計に従って編集
5. `src-tauri/tauri.conf.json` を上記設計に従って編集
6. `src-tauri/capabilities/default.json` を作成

### Phase 5: ビルドと実行

```bash
# 開発モードで実行
npm run tauri dev

# または
cargo tauri dev
```

### Phase 6: テスト手順

1. **日本語入力テスト**:
   - テキストボックスをクリック
   - fcitx5/mozcで日本語入力モードに切り替え
   - ひらがな入力 → 漢字変換を試す
   - 複数行にわたる日本語文章を入力

2. **クリップボード書き込みテスト**:
   - テキストボックスに「テストメッセージ」と入力
   - 「送信」ボタンをクリック
   - 別のアプリ（例: Kate）でCtrl+Vして内容を確認

3. **クリップボード読み込みテスト**:
   - 別のアプリで文字列をコピー
   - 「コピー」ボタンをクリック
   - テキストボックスに正しく表示されるか確認

4. **複数行テキストテスト**:
   - 複数行のテキストを入力
   - クリップボード経由で往復させる
   - 改行が保持されているか確認

5. **日本語往復テスト**:
   - 日本語文章を入力
   - クリップボードにコピー
   - テキストボックスをクリア
   - クリップボードから貼り付け
   - 文字化けせず正しく表示されるか確認

## 6. 期待される検証結果

### 成功シナリオ
✅ すべてのテストが成功した場合:
- Tauri + WebViewで日本語入力は問題なし
- クリップボード操作は公式プラグインで完全動作
- mini-text本体のTauri移植は技術的に問題なし

### 失敗シナリオと対応

#### IMEが動作しない場合
- **原因調査**: WebKitGTKのIME設定、環境変数確認
- **回避策**: GTK4実装の継続使用を推奨
- **結論**: Tauri移植は見送り

#### クリップボードが動作しない場合
- **原因調査**: プラグインのバージョン、権限設定確認
- **代替案**: コミュニティプラグイン（tauri-plugin-clipboard）を試す
- **最終手段**: shell pluginでxclipを使用（GTK4実装と同じアプローチ）

#### 部分的成功の場合
- IMEのみ問題 → GTK4継続
- クリップボードのみ問題 → 代替プラグインまたはxclip使用
- どちらも問題あり → Tauri移植は中止

## 7. ファイル一覧（実装後）

```
tauri/experiment/
├── ui/
│   ├── index.html          # メインUIファイル（人間が編集）
│   ├── styles.css          # スタイル定義（人間が編集）
│   └── script.js           # UIロジック（人間が編集）
├── src-tauri/
│   ├── Cargo.toml          # Rust依存関係
│   ├── tauri.conf.json     # Tauri設定（frontendDist="../ui"）
│   ├── build.rs            # ビルドスクリプト
│   ├── src/
│   │   └── main.rs         # Rustメインコード
│   ├── capabilities/
│   │   └── default.json    # セキュリティ設定
│   └── icons/              # アプリアイコン
├── package.json            # npm設定
├── package-lock.json       # npm依存関係ロック
└── README.md               # プロジェクト説明
```

## 8. トラブルシューティング

### ビルドエラー

**問題**: `tauri-plugin-clipboard-manager`が見つからない
```bash
# 解決策
cd src-tauri
cargo update
cargo build
```

**問題**: JavaScriptモジュールのインポートエラー
```bash
# 解決策: package.jsonにtypeを追加
{
  "type": "module",
  ...
}
```

### 実行時エラー

**問題**: Capabilityエラー
```
解決策: src-tauri/capabilities/default.jsonが正しく設定されているか確認
```

**問題**: クリップボード権限エラー
```
解決策: tauri.conf.jsonのpermissionsセクションを確認
```

### IMEテスト時の確認事項

- `GTK_IM_MODULE`環境変数が設定されているか
- fcitx5が起動しているか（`fcitx5-diagnose`で確認）
- WebKitGTKが最新版か（`apt list --installed | grep webkit`）

## 9. 次のステップ

### 検証成功後
1. 結果を`docs/research/tauri-experiment-results.md`に記録
2. Tauri移植の妥当性を再評価
3. 必要に応じて本体移植のPhase 1を開始

### 検証失敗後
1. 問題点を`docs/research/tauri-experiment-results.md`に詳細記録
2. GTK4実装の継続を決定
3. 代替技術スタックの検討（必要に応じて）

## 付録A: 参考資料

- Tauri v2公式ドキュメント: https://v2.tauri.app/
- Clipboard Manager Plugin: https://v2.tauri.app/plugin/clipboard/
- HTML/CSS/JS Template: https://v2.tauri.app/start/create-project/
- WebKitGTK: https://webkitgtk.org/

## 付録B: 設計の根拠

### なぜVanilla JS？
- **シンプル性**: フレームワーク不要で最小構成
- **学習コスト**: React/Vueなどの追加学習不要
- **検証目的**: IMEとクリップボードのみを検証、UIフレームワークは本質的でない
- **高速**: ビルド不要、即座にHTMLを編集して確認可能

### なぜ外部ファイル？
- **人間が編集可能**: HTML/CSS/JSを直接編集できる要件を満たす
- **保守性**: UIとロジックの分離
- **再利用性**: 他のプロジェクトへのコピーが容易

### なぜClipboard Managerプラグイン？
- **公式サポート**: Tauriチームが保守
- **クロスプラットフォーム**: Windows/macOS/Linuxで動作
- **シンプル**: readText/writeTextのみで十分
