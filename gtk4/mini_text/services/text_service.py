"""テキスト送受信統合サービス"""

import time
from typing import Optional, Protocol
from mini_text.utils.x11_command_executor import X11CommandExecutor
from mini_text.services.window_service import WindowService


class ClipboardServiceProtocol(Protocol):
    """クリップボードサービスのプロトコル（型ヒント用）"""

    def copy_to_clipboard(self, text: str) -> tuple[bool, str]:
        ...

    def get_from_clipboard(self) -> tuple[bool, str, str]:
        ...


class TextService:
    """テキスト送受信の統合サービス (SRP, DIP)"""

    def __init__(
        self,
        window_service: Optional[WindowService],
        clipboard_service: ClipboardServiceProtocol,
        executor: Optional[X11CommandExecutor] = None,
    ):
        """
        Args:
            window_service: ウィンドウ操作サービス（Noneの場合はデフォルトを使用）
            clipboard_service: クリップボード操作サービス
            executor: コマンド実行ユーティリティ（Noneの場合はデフォルトを使用）
        """
        self.executor = executor or X11CommandExecutor()
        self.window_service = window_service or WindowService(self.executor)
        self.clipboard_service = clipboard_service

    def send_text(
        self, window_id: str, text: str, activate_wait: float, key_wait: float
    ) -> tuple[bool, str]:
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
        # 1. クリップボードにテキストをコピー
        success, error_msg = self.clipboard_service.copy_to_clipboard(text)
        if not success:
            return False, error_msg

        # 2. ウィンドウをアクティブ化（activate_wait秒待機込み）
        success, error_msg = self.window_service.activate_window(
            window_id, activate_wait
        )
        if not success:
            return False, error_msg

        # 3. Ctrl+Vでペースト
        success, stdout, stderr = self.executor.execute(["xdotool", "key", "ctrl+v"])
        if not success:
            return False, f"ペースト操作に失敗しました: {stderr}"

        return True, ""

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
        # 1. Ctrl+A (全選択)
        success, stdout, stderr = self.executor.execute(["xdotool", "key", "ctrl+a"])
        if not success:
            return False, "", f"全選択操作に失敗しました: {stderr}"

        # 2. 待機
        time.sleep(key_wait)

        # 3. Ctrl+C (コピー)
        success, stdout, stderr = self.executor.execute(["xdotool", "key", "ctrl+c"])
        if not success:
            return False, "", f"コピー操作に失敗しました: {stderr}"

        # 4. 待機
        time.sleep(key_wait)

        # 5. クリップボードから取得
        success, text, error_msg = self.clipboard_service.get_from_clipboard()
        if not success:
            return False, "", error_msg

        return True, text, ""
