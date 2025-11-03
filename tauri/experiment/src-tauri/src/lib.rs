// Tauri Clipboard & IME Test Application
// このアプリケーションは、クリップボード操作とIME（日本語入力）の動作を検証します

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        // Clipboard Managerプラグインを初期化
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_opener::init())
        // greet commandは削除（今回は不要）
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
