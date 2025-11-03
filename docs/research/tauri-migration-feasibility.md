# mini-text の Tauri (Rust) 移植 - 技術的妥当性調査

**調査日**: 2025-11-03
**対象**: GTK4実装 (Phase 5完了) からTauriへの移植
**ステータス**: 実験的調査

## エグゼクティブサマリー

mini-textのGTK4実装からTauriへの移植は**技術的には可能**ですが、いくつかの重要な制約と課題があります。

### 結論
- ✅ **移植可能**: 全機能の実装は技術的に可能
- ⚠️ **注意点**: X11外部ウィンドウ操作にxdotoolが必須（Tauri単体では不可）
- 📊 **メリット**: バイナリサイズ削減（85MB→3MB）、起動時間改善（2s→0.5s）、メモリ使用量50%削減
- ⚠️ **デメリット**: 実装工数大、新技術スタック（Rust）、エコシステム未成熟

## 1. Tauriの基本的な特徴

### アーキテクチャ
- **バックエンド**: Rust（システムAPI、ビジネスロジック）
- **フロントエンド**: HTML/CSS/JavaScript（任意のフレームワーク: React, Vue, Svelte等）
- **レンダリング**: OSネイティブWebView
  - Linux: WebKitGTK
  - Windows: WebView2
  - macOS: WebKit

### パフォーマンス特性
| 項目 | GTK4/Python | Tauri/Rust |
|------|-------------|------------|
| バイナリサイズ | ~50-100MB (Pythonランタイム含む) | 2.5-3MB |
| 起動時間 | 1-2秒 | 0.5秒未満 |
| メモリ使用量 | 60-80MB | 30-40MB |
| リソース効率 | 中 | 高 |

### セキュリティ
- デフォルトで最小権限原則（Principle of Least Privilege）
- システムAPIアクセスはCapability設定で明示的に許可が必要
- Rustのメモリ安全性による脆弱性の削減

## 2. 機能別移植の妥当性分析

### 2.1 ウィンドウリスト取得・操作

**現在の実装** (`window_service.py`):
```python
# xdotoolで他のアプリケーションウィンドウを検索・操作
xdotool search --onlyvisible --name "."
xdotool getwindowname <window_id>
xdotool windowactivate --sync <window_id>
```

**Tauri移植の実現性**: ✅ **可能（xdotool経由）**

**実装方法**:
1. Tauri Shell Pluginを使用
2. xdotoolコマンドを外部プロセスとして実行
3. Rustバックエンドで結果を解析

**コード例** (Rust):
```rust
use tauri::command;
use std::process::Command;

#[command]
async fn get_window_list() -> Result<Vec<(String, String)>, String> {
    // xdotoolでウィンドウID一覧を取得
    let output = Command::new("xdotool")
        .args(&["search", "--onlyvisible", "--name", "."])
        .output()
        .map_err(|e| e.to_string())?;

    let window_ids: Vec<String> = String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(|s| s.to_string())
        .collect();

    // 各ウィンドウのタイトルを取得
    let mut results = Vec::new();
    for window_id in window_ids {
        let output = Command::new("xdotool")
            .args(&["getwindowname", &window_id])
            .output()
            .map_err(|e| e.to_string())?;

        let title = String::from_utf8_lossy(&output.stdout).trim().to_string();
        if !title.is_empty() {
            results.push((window_id, title));
        }
    }

    Ok(results)
}
```

**重要な制約**:
- **xdotoolへの依存は継続**: Tauriには他アプリウィンドウ操作のネイティブAPIなし
- **X11専用**: Waylandでは動作しない（GTK4実装と同じ制約）
- **セキュリティ設定**: `tauri.conf.json`でshellプラグインとxdotool実行を許可する必要あり

### 2.2 クリップボード操作

**現在の実装** (`gtk_clipboard_service.py`):
```python
# GTK4 Gdk.Clipboard APIを使用
clipboard.set(text)  # 書き込み
clipboard.read_text_async()  # 読み込み（非同期）
```

**Tauri移植の実現性**: ✅ **可能（ネイティブサポート）**

**実装方法**:
Tauri公式Clipboardプラグインを使用（クロスプラットフォーム対応）

**コード例** (Rust + JavaScript):

Rust側:
```rust
use tauri_plugin_clipboard_manager::ClipboardExt;

#[command]
async fn copy_to_clipboard(app_handle: tauri::AppHandle, text: String) -> Result<(), String> {
    app_handle.clipboard().write_text(text)
        .map_err(|e| e.to_string())
}

#[command]
async fn get_from_clipboard(app_handle: tauri::AppHandle) -> Result<String, String> {
    app_handle.clipboard().read_text()
        .map_err(|e| e.to_string())
}
```

JavaScript側:
```javascript
import { writeText, readText } from '@tauri-apps/plugin-clipboard-manager';

await writeText('送信するテキスト');
const text = await readText();
```

**メリット**:
- xclip不要（GTK4実装と同様）
- クロスプラットフォーム対応
- 非同期APIがネイティブサポート
- コミュニティプラグインでHTML/RTF/画像もサポート可能

### 2.3 キーボード入力シミュレーション

**現在の実装**:
```python
# Ctrl+V でペースト
xdotool key ctrl+v
# Ctrl+A, Ctrl+C で全選択・コピー
xdotool key ctrl+a
xdotool key ctrl+c
```

**Tauri移植の実現性**: ✅ **可能（xdotool経由）**

**実装方法**:
Shell Pluginでxdotoolを実行（ウィンドウ操作と同じアプローチ）

```rust
#[command]
async fn send_keys(keys: String) -> Result<(), String> {
    Command::new("xdotool")
        .args(&["key", &keys])
        .output()
        .map_err(|e| e.to_string())?;
    Ok(())
}
```

### 2.4 設定管理

**現在の実装** (`config_manager.py`):
- JSON設定ファイル: `~/.config/mini-text/config.json`
- タイミング設定、ウィンドウサイズ保存

**Tauri移植の実現性**: ✅ **可能（改善の余地あり）**

**実装方法**:
1. Rust標準ライブラリで実装（現在と同等）
2. または `tauri-plugin-store`を使用（Key-Valueストア）

```rust
use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Serialize, Deserialize)]
struct Config {
    window: WindowConfig,
    timing: TimingConfig,
}

#[derive(Serialize, Deserialize)]
struct TimingConfig {
    window_activate_wait: f32,
    key_input_wait: f32,
    copyfrom_wait: f32,
}

#[command]
fn load_config() -> Result<Config, String> {
    let config_path = dirs::config_dir()
        .ok_or("設定ディレクトリが見つかりません")?
        .join("mini-text")
        .join("config.json");

    let content = fs::read_to_string(&config_path)
        .map_err(|e| e.to_string())?;

    serde_json::from_str(&content)
        .map_err(|e| e.to_string())
}
```

**メリット**:
- 型安全性（Rust + serde）
- 既存設定ファイルとの互換性維持可能

## 3. アーキテクチャ移植マッピング

### 現在のGTK4アーキテクチャ
```
┌─────────────────────────────────────┐
│ UI Layer (GTK4 + Python)            │
│ - MainWindow (Gtk.ApplicationWindow)│
│ - SettingsDialog                    │
└─────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────┐
│ Service Layer (Python)              │
│ - TextService                       │
│ - WindowService                     │
│ - GtkClipboardService               │
└─────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────┐
│ Utils Layer (Python)                │
│ - X11CommandExecutor (subprocess)   │
│ - ConfigManager (JSON)              │
└─────────────────────────────────────┘
              │
              ↓
        xdotool (外部コマンド)
```

### Tauri移植後のアーキテクチャ
```
┌─────────────────────────────────────┐
│ Frontend (HTML/CSS/JS)              │
│ - React/Vue/Svelte/Vanilla          │
│ - UI Components                     │
└─────────────────────────────────────┘
              │ (IPC via @tauri-apps/api)
              ↓
┌─────────────────────────────────────┐
│ Backend (Rust)                      │
│ - Tauri Commands (#[command])       │
│ - Service Layer                     │
│   - TextService                     │
│   - WindowService                   │
│   - ClipboardService (Plugin)       │
│ - ConfigManager (serde_json)        │
└─────────────────────────────────────┘
              │
              ↓
    ┌─────────────────────┐
    │ Tauri Plugins       │
    ├─────────────────────┤
    │ - shell (xdotool)   │
    │ - clipboard-manager │
    └─────────────────────┘
              │
              ↓
        xdotool (外部コマンド)
```

### レイヤーマッピング

| GTK4 Layer | Tauri Layer | 実装言語 | 備考 |
|------------|-------------|----------|------|
| UI Layer (GTK4) | Frontend (Web) | Python → HTML/JS | 完全な再実装が必要 |
| Service Layer | Rust Commands | Python → Rust | ロジックは流用可能 |
| Utils Layer | Rust Utilities | Python → Rust | subprocess → std::process::Command |
| Config (JSON) | Rust + serde | Python → Rust | フォーマット互換性維持可能 |

## 4. 移植の課題と解決策

### 課題1: フロントエンド再実装

**問題**:
- GTK4のUI（`.ui`ファイル + Python）からHTML/CSS/JSへの完全な再実装が必要
- IME統合も再度確認が必要（WebViewのIME対応）

**解決策**:
- シンプルなVanilla JS実装から開始（フレームワーク不要）
- 既存のUIデザインを参考にHTML/CSSで再現
- WebViewはネイティブIME統合があるため、日本語入力は問題ない可能性が高い

**工数**: 大（UI全体の再構築）

### 課題2: 非同期処理モデルの違い

**問題**:
- Python: 同期処理中心（`time.sleep()`、同期ラッパー）
- Rust: 非同期中心（`async/await`、`tokio`ランタイム）

**解決策**:
- Tauri Commandsは`async fn`として実装
- `tokio::time::sleep()`で待機時間を実装
- フロントエンドは全てPromise/async-await

```rust
#[command]
async fn send_text(window_id: String, text: String, activate_wait: f32) -> Result<(), String> {
    // クリップボードにコピー
    copy_to_clipboard(text).await?;

    // ウィンドウをアクティブ化
    activate_window(window_id).await?;

    // 待機
    tokio::time::sleep(tokio::time::Duration::from_secs_f32(activate_wait)).await;

    // Ctrl+V
    send_keys("ctrl+v").await?;

    Ok(())
}
```

### 課題3: Python依存ライブラリの移植

**問題**:
- `pytest`のテストをRustに移植
- PyGObjectなどのPython固有ライブラリの代替

**解決策**:
- Rust標準テスト: `#[cfg(test)]` + `cargo test`
- モック: `mockall` crateを使用
- 既存のテストロジックを参考に実装

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_get_window_list() {
        let result = get_window_list().await;
        assert!(result.is_ok());
    }
}
```

### 課題4: エコシステムの成熟度

**問題**:
- Tauriはまだ比較的新しい（2.0が2025年リリース）
- GTK4/Pythonほどドキュメント・事例が豊富でない

**解決策**:
- 公式ドキュメント活用: https://v2.tauri.app/
- コミュニティプラグイン活用
- 必要に応じてRust cratesを直接使用

## 5. メリット・デメリット比較

### Tauri移植のメリット

#### パフォーマンス
- ✅ **バイナリサイズ**: 85MB → 3MB（約97%削減）
- ✅ **起動時間**: 2秒 → 0.5秒未満（4倍高速化）
- ✅ **メモリ使用量**: 60-80MB → 30-40MB（50%削減）
- ✅ **CPU効率**: Rustのゼロコスト抽象化

#### セキュリティ
- ✅ Rustのメモリ安全性
- ✅ デフォルトで最小権限原則
- ✅ 定期的なセキュリティ監査

#### クロスプラットフォーム
- ✅ Windows/macOS対応の可能性（xdotoolは不要な代替実装で）
- ✅ 単一バイナリ配布

#### 開発者体験
- ✅ 型安全性（Rust + TypeScript）
- ✅ モダンなフロントエンド開発（React/Vue/Svelte）
- ✅ 統合されたビルドツール（Tauri CLI）

### Tauri移植のデメリット

#### 技術的課題
- ❌ **UI完全再実装**: GTK4 → HTML/CSS/JS（工数大）
- ❌ **新技術スタック**: Rust学習曲線
- ❌ **xdotool依存継続**: 外部ウィンドウ操作は依然として外部コマンド経由
- ❌ **非同期複雑性**: Pythonより非同期処理が複雑

#### 機能面
- ⚠️ **IME統合**: WebViewのIME対応は確認が必要（おそらく問題なし）
- ⚠️ **ネイティブルック**: GTK4よりWebViewベースのUIは「ネイティブ感」が劣る可能性

#### 開発面
- ❌ **実装工数**: 全体で数週間〜1ヶ月以上
- ❌ **エコシステム**: Python/GTK4より未成熟
- ❌ **デバッグ**: Rust + JS のデバッグは2層構造

## 6. 推奨事項

### 推奨: GTK4実装の継続使用

**理由**:
1. **現在の実装は安定**: Phase 5完了、全機能動作確認済み
2. **工数対効果**: 移植のメリット（サイズ・速度）はmini-textの用途では必須ではない
3. **技術的優位性**: GTK4はLinuxネイティブ、IME統合済み
4. **保守性**: Pythonはシンプルで読みやすく、保守しやすい

### 実験的移植の価値

Tauri移植は以下の目的で**学習実験として有用**:
- ✅ Rust/Tauri技術の習得
- ✅ クロスプラットフォーム展開の検証
- ✅ パフォーマンス最適化の研究
- ✅ モダンWebフロントエンド統合の経験

### 移植を検討すべきケース

以下の場合にTauri移植を検討する価値がある:
1. **Windows/macOS対応が必要**になった場合
2. **バイナリ配布**が必要になった場合（パッケージング）
3. **パフォーマンスがボトルネック**になった場合（現状は問題なし）
4. **Rust/Webスキル習得**が目的の場合

## 7. PoC（概念実証）実装計画案

もし実験的移植を行う場合の段階的アプローチ:

### Phase 1: 最小構成（1-2週間）
- [ ] Tauriプロジェクト初期化
- [ ] 基本UI（ウィンドウリスト表示のみ）
- [ ] xdotool経由でウィンドウリスト取得
- [ ] 動作確認

### Phase 2: 基本機能（1-2週間）
- [ ] クリップボード統合（Tauri Plugin）
- [ ] テキスト送信機能実装
- [ ] 設定管理（JSON）実装

### Phase 3: 完全機能（1-2週間）
- [ ] テキスト受信機能
- [ ] 設定ダイアログUI
- [ ] エラーハンドリング
- [ ] 日本語/IMEテスト

### Phase 4: 最適化（1週間）
- [ ] パフォーマンス測定
- [ ] バイナリサイズ最適化
- [ ] テスト実装（Rust + JS）

**合計工数見積もり**: 4-7週間

## 8. 結論

### 技術的妥当性: ✅ 可能

mini-textのGTK4実装からTauriへの移植は**技術的に完全に実現可能**です。全ての機能（ウィンドウ操作、クリップボード、キー送信、設定管理）について、Tauriで実装可能な方法が確認できました。

### 実用的推奨: ⚠️ 慎重に判断

**現状維持を推奨**します。理由:
- GTK4実装は既に安定稼働中
- Linuxデスクトップ用途ではGTK4がベストチョイス
- 移植の工数対効果が低い（現状で性能問題なし）

**移植を推奨する条件**:
- クロスプラットフォーム対応が必要
- Rust/Tauri技術の習得が目的
- 学習実験として価値を見出す場合

### 実験的実装の価値: ✅ 高い

学習目的や技術検証としてTauri移植を行うことは**非常に有意義**です:
- モダンな技術スタックの経験
- Rust言語の実践的習得
- クロスプラットフォームGUI開発の知見
- 異なるアーキテクチャの比較

## 参考資料

### Tauri公式ドキュメント
- Tauri v2: https://v2.tauri.app/
- Shell Plugin: https://v2.tauri.app/plugin/shell/
- Clipboard Plugin: https://v2.tauri.app/plugin/clipboard/

### 比較資料
- Tauri vs Electron 2025: https://codeology.co.nz/articles/tauri-vs-electron-2025-desktop-development.html
- Tauri Performance: https://www.gethopp.app/blog/tauri-vs-electron

### 関連技術
- xdotool: https://www.semicomplete.com/projects/xdotool/
- WebKitGTK: https://webkitgtk.org/
- Rust async book: https://rust-lang.github.io/async-book/
