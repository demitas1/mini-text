// Tauri Clipboard & IME Test Application
// このアプリケーションは、クリップボード操作とIME（日本語入力）の動作を検証します

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
        // Clipboard Managerプラグインを初期化
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_opener::init())
        // copyfrom コマンドを登録
        .invoke_handler(tauri::generate_handler![copy_from_active_window])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
