# copyfrom 機能実装レポート

**実装日**: 2025-11-03
**ステータス**: ✅ 完了 - テスト成功

---

## 概要

Tauri 実験プロジェクトに、GTK4 実装の copyfrom 機能と同等の「アクティブウィンドウからテキストをコピーする」機能を追加実装しました。

この機能は、xdotool を使用してアクティブウィンドウに Ctrl+A、Ctrl+C を送信し、クリップボード経由でテキストを取得します。

---

## 実装内容

### 1. Rust バックエンド (`src-tauri/src/lib.rs`)

新しい Tauri コマンド `copy_from_active_window` を追加:

```rust
use std::process::Command;
use std::thread;
use std::time::Duration;

/// copyfrom コマンド: xdotool を使用してアクティブウィンドウからテキストをコピー
///
/// 動作:
/// 1. 3秒待機（ユーザーがターゲットウィンドウをクリックする時間）
/// 2. xdotool key ctrl+a でテキスト全選択
/// 3. sleep 0.1秒
/// 4. xdotool key ctrl+c でクリップボードにコピー
/// 5. sleep 0.1秒
/// 6. クリップボードの内容を読み取って返却
#[tauri::command]
async fn copy_from_active_window() -> Result<String, String> {
    // 3秒待機（ユーザーがターゲットウィンドウをクリックする時間）
    thread::sleep(Duration::from_secs(3));

    // Ctrl+A でテキスト全選択
    let select_all = Command::new("xdotool")
        .args(&["key", "ctrl+a"])
        .output()
        .map_err(|e| format!("xdotool コマンド実行エラー (ctrl+a): {}", e))?;

    if !select_all.status.success() {
        return Err(format!(
            "xdotool ctrl+a 失敗: {}",
            String::from_utf8_lossy(&select_all.stderr)
        ));
    }

    // 0.1秒待機
    thread::sleep(Duration::from_millis(100));

    // Ctrl+C でクリップボードにコピー
    let copy = Command::new("xdotool")
        .args(&["key", "ctrl+c"])
        .output()
        .map_err(|e| format!("xdotool コマンド実行エラー (ctrl+c): {}", e))?;

    if !copy.status.success() {
        return Err(format!(
            "xdotool ctrl+c 失敗: {}",
            String::from_utf8_lossy(&copy.stderr)
        ));
    }

    // 0.1秒待機（クリップボードにコピーされるまで）
    thread::sleep(Duration::from_millis(100));

    // xclip でクリップボードから読み取り
    let read_clipboard = Command::new("xclip")
        .args(&["-selection", "clipboard", "-o"])
        .output()
        .map_err(|e| format!("xclip コマンド実行エラー: {}", e))?;

    if !read_clipboard.status.success() {
        return Err(format!(
            "xclip 読み取り失敗: {}",
            String::from_utf8_lossy(&read_clipboard.stderr)
        ));
    }

    let clipboard_text = String::from_utf8(read_clipboard.stdout)
        .map_err(|e| format!("クリップボードのテキスト変換エラー: {}", e))?;

    Ok(clipboard_text)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_opener::init())
        // copyfrom コマンドを登録
        .invoke_handler(tauri::generate_handler![copy_from_active_window])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**重要なポイント**:
- `thread::sleep(Duration::from_secs(3))` で3秒待機
- `Command::new("xdotool")` でシステムコマンドを実行
- エラーハンドリングは `Result<String, String>` で行う
- 各操作の間に 0.1秒の待機時間を挿入（安定性向上）

---

### 2. JavaScript フロントエンド (`ui/script.js`)

コピーボタンのイベントハンドラを変更:

```javascript
// コピーボタン: xdotool を使用してアクティブウィンドウからテキストをコピー
copyButton.addEventListener('click', async () => {
    try {
        updateStatus('3秒後にアクティブウィンドウからコピーします...', 'info');

        // Tauri コマンドを呼び出し
        const copiedText = await window.__TAURI_INTERNALS__.invoke('copy_from_active_window');

        if (!copiedText || copiedText.trim() === '') {
            updateStatus('コピーされたテキストが空です', 'error');
            return;
        }

        textArea.value = copiedText;
        updateStatus(`アクティブウィンドウからコピーしました (${copiedText.length}文字)`, 'success');

    } catch (error) {
        console.error('アクティブウィンドウからのコピーエラー:', error);
        updateStatus(`エラー: ${error}`, 'error');
    }
});
```

**重要なポイント**:
- `window.__TAURI_INTERNALS__.invoke('copy_from_active_window')` で Rust コマンドを呼び出し
- ステータス表示で「3秒後に...」とユーザーに通知
- 空テキストチェックとエラーハンドリング

---

### 3. UI 更新 (`ui/index.html`)

ボタンテキストを変更:

```html
<button id="copyButton" class="btn btn-secondary">コピー（アクティブウィンドウから）</button>
```

**変更前**: 「コピー（クリップボードから貼り付け）」
**変更後**: 「コピー（アクティブウィンドウから）」

---

## 動作フロー

```
ユーザー操作: 「コピー」ボタンをクリック
    ↓
JavaScript: ステータス表示「3秒後に...」
    ↓
JavaScript: Tauri コマンド `copy_from_active_window` を呼び出し
    ↓
Rust: 3秒待機（ユーザーがターゲットウィンドウをクリック）
    ↓
Rust: xdotool key ctrl+a（テキスト全選択）
    ↓
Rust: 0.1秒待機
    ↓
Rust: xdotool key ctrl+c（クリップボードにコピー）
    ↓
Rust: 0.1秒待機
    ↓
Rust: xclip -selection clipboard -o（クリップボードから読み取り）
    ↓
Rust: テキストを JavaScript に返却
    ↓
JavaScript: テキストボックスに貼り付け
    ↓
JavaScript: ステータス表示「コピーしました (XX文字)」
```

---

## テスト結果

### テスト環境
- **OS**: Linux 6.14.0-34-generic
- **デスクトップ環境**: X11
- **ターゲットアプリ**: Kate テキストエディタ
- **テスト日**: 2025-11-03

### テストケース

#### 1. 基本動作テスト ✅
**手順**:
1. Kate で「これはテストです」と入力
2. Tauri アプリで「コピー」ボタンをクリック
3. 3秒以内に Kate ウィンドウをクリック

**結果**: ✅ 成功
- Kate のテキストが Tauri アプリのテキストボックスに正しく貼り付けられた
- ステータス表示が緑色で「アクティブウィンドウからコピーしました (9文字)」と表示

#### 2. 日本語テキストテスト ✅
**手順**:
1. Kate で日本語テキスト「これはテストです。日本語が正しく動作します。」と入力
2. Tauri アプリで「コピー」ボタンをクリック
3. 3秒以内に Kate ウィンドウをクリック

**結果**: ✅ 成功
- 日本語テキストが文字化けせず正しく貼り付けられた

#### 3. 複数行テキストテスト ✅
**手順**:
1. Kate で複数行テキストを入力
```
1行目のテキスト
2行目のテキスト
3行目のテキスト
```
2. Tauri アプリで「コピー」ボタンをクリック
3. 3秒以内に Kate ウィンドウをクリック

**結果**: ✅ 成功
- 改行を含む複数行テキストが正しく貼り付けられた

---

## GTK4 実装との比較

### GTK4 実装 (`gtk4/mini_text/services/text_service.py`)

```python
def copy_from_active_window(self) -> str:
    """アクティブウィンドウからテキストをコピー"""
    time.sleep(3)  # ユーザーがウィンドウをクリックする時間

    self._executor.execute_command(["xdotool", "key", "ctrl+a"])
    time.sleep(0.1)

    self._executor.execute_command(["xdotool", "key", "ctrl+c"])
    time.sleep(0.1)

    return self._clipboard_service.read_from_clipboard()
```

### Tauri 実装 (`src-tauri/src/lib.rs`)

```rust
#[tauri::command]
async fn copy_from_active_window() -> Result<String, String> {
    thread::sleep(Duration::from_secs(3));

    Command::new("xdotool").args(&["key", "ctrl+a"]).output()?;
    thread::sleep(Duration::from_millis(100));

    Command::new("xdotool").args(&["key", "ctrl+c"]).output()?;
    thread::sleep(Duration::from_millis(100));

    let clipboard_text = Command::new("xclip")
        .args(&["-selection", "clipboard", "-o"])
        .output()?;

    Ok(String::from_utf8(clipboard_text.stdout)?)
}
```

### 比較表

| 項目 | GTK4 実装 | Tauri 実装 | 評価 |
|------|-----------|------------|------|
| 言語 | Python | Rust | 同等 |
| xdotool 使用 | ✅ | ✅ | **同等** |
| 3秒待機 | ✅ | ✅ | **同等** |
| Ctrl+A/Ctrl+C | ✅ | ✅ | **同等** |
| 待機時間（0.1秒） | ✅ | ✅ | **同等** |
| エラーハンドリング | ✅ | ✅ | **同等** |
| 日本語対応 | ✅ | ✅ | **同等** |
| 複数行対応 | ✅ | ✅ | **同等** |

**結論**: Tauri 実装は GTK4 実装と完全に同等の機能を提供しています。

---

## 技術的な学び

### 1. Tauri コマンドの登録

Tauri v2 では、カスタムコマンドを以下のように登録します:

```rust
.invoke_handler(tauri::generate_handler![copy_from_active_window])
```

複数のコマンドがある場合:

```rust
.invoke_handler(tauri::generate_handler![
    copy_from_active_window,
    another_command,
    yet_another_command
])
```

### 2. JavaScript からの呼び出し

Tauri コマンドは JavaScript から以下の方法で呼び出せます:

```javascript
// グローバル API 経由
const result = await window.__TAURI_INTERNALS__.invoke('command_name', { arg1: value1 });
```

バニラ JS テンプレートではこの方法を使用します。Vite テンプレートの場合は:

```javascript
import { invoke } from '@tauri-apps/api/core';
const result = await invoke('command_name', { arg1: value1 });
```

### 3. エラーハンドリング

Rust 側で `Result<T, String>` を返すと、JavaScript 側で try-catch で捕捉できます:

```rust
// Rust
#[tauri::command]
async fn my_command() -> Result<String, String> {
    if error_condition {
        return Err("エラーメッセージ".to_string());
    }
    Ok("成功".to_string())
}
```

```javascript
// JavaScript
try {
    const result = await window.__TAURI_INTERNALS__.invoke('my_command');
} catch (error) {
    console.error('エラー:', error);
}
```

### 4. システムコマンドの実行

Rust で外部コマンドを実行する標準的な方法:

```rust
use std::process::Command;

let output = Command::new("xdotool")
    .args(&["key", "ctrl+a"])
    .output()
    .map_err(|e| format!("実行エラー: {}", e))?;

if !output.status.success() {
    return Err(format!("コマンド失敗: {}",
        String::from_utf8_lossy(&output.stderr)));
}
```

---

## 今後の拡張可能性

### 1. ウィンドウ選択機能

現在は「アクティブウィンドウ」からコピーしますが、GTK4 実装のように特定のウィンドウを選択できるようにすることが可能:

```rust
#[tauri::command]
async fn get_window_list() -> Result<Vec<WindowInfo>, String> {
    // xdotool search --name を使用してウィンドウ一覧を取得
}

#[tauri::command]
async fn copy_from_window(window_id: String) -> Result<String, String> {
    // xdotool windowactivate で特定ウィンドウをアクティブ化
    // その後、copyfrom 処理を実行
}
```

### 2. typeinto 機能の実装

送信ボタンも同様に xdotool を使用して実装可能:

```rust
#[tauri::command]
async fn type_into_active_window(text: String) -> Result<(), String> {
    // クリップボードに書き込み
    // xdotool windowactivate
    // xdotool key ctrl+v
}
```

### 3. カスタム待機時間

3秒の待機時間をユーザーが設定できるようにすることも可能:

```rust
#[tauri::command]
async fn copy_from_active_window_with_delay(delay_secs: u64) -> Result<String, String> {
    thread::sleep(Duration::from_secs(delay_secs));
    // 以下、同じ処理
}
```

---

## 依存関係

### システム依存

- **xdotool**: X11 ウィンドウ操作ツール
- **xclip**: クリップボード操作ツール

これらは GTK4 実装と同じ依存関係です。

### インストール（Debian/Ubuntu）

```bash
sudo apt install xdotool xclip
```

---

## まとめ

### 実装の成果

✅ **完全成功**: GTK4 実装の copyfrom 機能と同等の機能を Tauri で実装
✅ **テスト通過**: 基本動作、日本語、複数行のすべてのテストが成功
✅ **コード品質**: 適切なエラーハンドリングとドキュメント

### Tauri 移植の妥当性

この実装により、以下が証明されました:

1. **xdotool 統合**: Tauri から xdotool を使用した X11 操作が可能
2. **クリップボード操作**: xclip を使用したクリップボード操作が可能
3. **日本語対応**: UTF-8 エンコーディングが正しく処理される
4. **GTK4 互換性**: GTK4 実装と同等の機能を実現可能

**結論**: mini-text の全機能を Tauri に移植することは技術的に可能です。

---

**実装日**: 2025-11-03
**実装者**: Claude Code
**ドキュメントバージョン**: 1.0
