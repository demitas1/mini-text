"""クリップボード操作サービス"""

from typing import Optional
from mini_text.utils.x11_command_executor import X11CommandExecutor


class ClipboardService:
    """クリップボード操作サービス (SRP)"""

    def __init__(self, executor: Optional[X11CommandExecutor] = None):
        """
        Args:
            executor: コマンド実行ユーティリティ（Noneの場合はデフォルトを使用）
        """
        self.executor = executor or X11CommandExecutor()

    def copy_to_clipboard(self, text: str) -> tuple[bool, str]:
        """
        クリップボードにテキストをコピー

        Args:
            text: コピーするテキスト

        Returns:
            tuple[bool, str]: (成功したか, エラーメッセージ)
        """
        # xclip -i -selection clipboard でクリップボードにコピー
        # -i フラグで明示的に入力モードを指定
        success, stdout, stderr = self.executor.execute(
            ["xclip", "-i", "-selection", "clipboard"], input_data=text
        )

        if not success:
            return False, f"クリップボードへのコピーに失敗しました: {stderr}"

        return True, ""

    def get_from_clipboard(self) -> tuple[bool, str, str]:
        """
        クリップボードからテキストを取得

        Returns:
            tuple[bool, str, str]: (成功したか, テキスト, エラーメッセージ)
        """
        # xclip -selection clipboard -o でクリップボードから取得
        success, stdout, stderr = self.executor.execute(
            ["xclip", "-selection", "clipboard", "-o"]
        )

        if not success:
            return False, "", f"クリップボードからの取得に失敗しました: {stderr}"

        return True, stdout, ""
