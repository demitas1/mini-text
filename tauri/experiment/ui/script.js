// Tauri APIをグローバルオブジェクトから取得
const { writeText, readText } = window.__TAURI_PLUGIN_CLIPBOARD_MANAGER__;

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
