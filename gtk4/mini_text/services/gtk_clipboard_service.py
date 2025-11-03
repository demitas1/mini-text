"""GTK4 Gdk.Clipboardを使用したクリップボードサービス"""

from typing import Optional
import time
import gi

gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, GLib


class GtkClipboardService:
    """GTK4 Gdk.Clipboardを使用したクリップボード操作サービス (SRP)"""

    def __init__(self, clipboard: Optional[Gdk.Clipboard] = None):
        """
        Args:
            clipboard: Gdk.Clipboardインスタンス（Noneの場合はデフォルトを使用）
        """
        if clipboard is None:
            display = Gdk.Display.get_default()
            if display is None:
                raise RuntimeError("デフォルトディスプレイが取得できません")
            self.clipboard = display.get_clipboard()
        else:
            self.clipboard = clipboard

    def copy_to_clipboard(self, text: str) -> tuple[bool, str]:
        """
        クリップボードにテキストをコピー（同期）

        Args:
            text: コピーするテキスト

        Returns:
            tuple[bool, str]: (成功したか, エラーメッセージ)
        """
        try:
            self.clipboard.set(text)
            return True, ""
        except Exception as e:
            return False, f"クリップボードへのコピーに失敗しました: {str(e)}"

    def get_from_clipboard(self) -> tuple[bool, str, str]:
        """
        クリップボードからテキストを取得（同期）

        注意: GTK4のAPIは非同期のみだが、GLib.MainContextを使用して
        メインループを回しながら同期的に待機

        Returns:
            tuple[bool, str, str]: (成功したか, テキスト, エラーメッセージ)
        """
        try:
            # 結果を格納する変数
            result = {"text": None, "error": None, "done": False}

            def on_read_finish(_clipboard, async_result):
                """非同期読み込み完了時のコールバック"""
                try:
                    text = self.clipboard.read_text_finish(async_result)
                    result["text"] = text if text is not None else ""
                except Exception as e:
                    result["error"] = str(e)
                finally:
                    result["done"] = True

            # 非同期読み込み開始
            self.clipboard.read_text_async(None, on_read_finish)

            # メインループを回しながら完了を待機
            context = GLib.MainContext.default()
            timeout = 5.0  # 5秒タイムアウト
            start_time = time.time()

            while not result["done"]:
                # メインコンテキストのイベントを処理
                while context.pending():
                    context.iteration(False)

                # タイムアウトチェック
                if time.time() - start_time > timeout:
                    return False, "", "クリップボードからの取得がタイムアウトしました"

                # CPU負荷を下げるため短時間スリープ
                time.sleep(0.01)

            if result["error"]:
                return (
                    False,
                    "",
                    f"クリップボードからの取得に失敗しました: {result['error']}",
                )

            return True, result["text"], ""

        except Exception as e:
            return False, "", f"クリップボードからの取得に失敗しました: {str(e)}"
