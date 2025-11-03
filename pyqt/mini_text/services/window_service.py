"""ウィンドウ操作サービス"""

import time
from typing import Optional
from mini_text.utils.x11_command_executor import X11CommandExecutor


class WindowService:
    """ウィンドウ操作サービス (SRP)"""

    def __init__(self, executor: Optional[X11CommandExecutor] = None):
        """
        Args:
            executor: コマンド実行ユーティリティ（Noneの場合はデフォルトを使用）
        """
        self.executor = executor or X11CommandExecutor()

    def get_window_list(self) -> list[tuple[str, str]]:
        """
        現在開いているウィンドウの一覧を取得

        Returns:
            list[tuple[str, str]]: [(window_id, window_name), ...]
        """
        # xdotool search でデスクトップ上の全ウィンドウを検索
        success, stdout, stderr = self.executor.execute(
            ["xdotool", "search", "--onlyvisible", "--name", "."]
        )

        if not success:
            return []

        # ウィンドウIDのリストを取得
        window_ids = [line.strip() for line in stdout.split("\n") if line.strip()]

        result = []
        for window_id in window_ids:
            # 各ウィンドウのタイトルを取得
            success, title, stderr = self.executor.execute(
                ["xdotool", "getwindowname", window_id]
            )

            if success and title.strip():
                result.append((window_id, title.strip()))

        return result

    def activate_window(self, window_id: str, wait_time: float) -> tuple[bool, str]:
        """
        指定したウィンドウをアクティブ化

        Args:
            window_id: アクティブ化するウィンドウのID
            wait_time: アクティブ化後の待機時間(秒)

        Returns:
            tuple[bool, str]: (成功したか, エラーメッセージ)
        """
        # xdotool windowactivate でウィンドウをアクティブ化
        success, stdout, stderr = self.executor.execute(
            ["xdotool", "windowactivate", "--sync", window_id]
        )

        if not success:
            return False, f"ウィンドウのアクティブ化に失敗しました: {stderr}"

        # 指定時間待機
        if wait_time > 0:
            time.sleep(wait_time)

        return True, ""
