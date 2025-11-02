"""TextServiceのユニットテスト"""

import unittest
from unittest.mock import Mock
from mini_text.services.text_service import TextService


class TestTextService(unittest.TestCase):
    """TextServiceのテストケース"""

    def setUp(self):
        """各テストの前に実行される準備処理"""
        # モックを作成
        self.mock_executor = Mock()
        self.mock_window_service = Mock()
        self.mock_clipboard_service = Mock()

        self.service = TextService(
            window_service=self.mock_window_service,
            clipboard_service=self.mock_clipboard_service,
            executor=self.mock_executor,
        )

    def test_send_text_success(self):
        """テキスト送信が成功することを確認"""
        # 各サービスのモック戻り値を設定
        self.mock_clipboard_service.copy_to_clipboard.return_value = (True, "")
        self.mock_window_service.activate_window.return_value = (True, "")
        self.mock_executor.execute.return_value = (True, "", "")

        success, error_msg = self.service.send_text("12345", "テストテキスト", 0.1, 0.1)

        # 成功することを確認
        self.assertTrue(success)
        self.assertEqual(error_msg, "")

        # 各サービスが正しく呼ばれたことを確認
        self.mock_clipboard_service.copy_to_clipboard.assert_called_once_with(
            "テストテキスト"
        )
        self.mock_window_service.activate_window.assert_called_once_with("12345", 0.1)
        self.mock_executor.execute.assert_called_once_with(
            ["xdotool", "key", "ctrl+v"]
        )

    def test_send_text_clipboard_failure(self):
        """クリップボードコピー失敗時の処理を確認"""
        # クリップボードコピーが失敗
        self.mock_clipboard_service.copy_to_clipboard.return_value = (
            False,
            "クリップボードエラー",
        )

        success, error_msg = self.service.send_text("12345", "テストテキスト", 0.1, 0.1)

        # 失敗することを確認
        self.assertFalse(success)
        self.assertIn("クリップボードエラー", error_msg)

        # ウィンドウアクティベートは実行されないことを確認
        self.mock_window_service.activate_window.assert_not_called()

    def test_send_text_activate_failure(self):
        """ウィンドウアクティベート失敗時の処理を確認"""
        # クリップボードコピーは成功、アクティベートが失敗
        self.mock_clipboard_service.copy_to_clipboard.return_value = (True, "")
        self.mock_window_service.activate_window.return_value = (
            False,
            "ウィンドウエラー",
        )

        success, error_msg = self.service.send_text("12345", "テストテキスト", 0.1, 0.1)

        # 失敗することを確認
        self.assertFalse(success)
        self.assertIn("ウィンドウエラー", error_msg)

        # ペースト操作は実行されないことを確認
        self.mock_executor.execute.assert_not_called()

    def test_send_text_paste_failure(self):
        """ペースト操作失敗時の処理を確認"""
        # クリップボードとアクティベートは成功、ペーストが失敗
        self.mock_clipboard_service.copy_to_clipboard.return_value = (True, "")
        self.mock_window_service.activate_window.return_value = (True, "")
        self.mock_executor.execute.return_value = (False, "", "ペーストエラー")

        success, error_msg = self.service.send_text("12345", "テストテキスト", 0.1, 0.1)

        # 失敗することを確認
        self.assertFalse(success)
        self.assertIn("ペースト操作に失敗", error_msg)

    def test_receive_text_success(self):
        """テキスト受信が成功することを確認"""
        # 各操作のモック戻り値を設定
        self.mock_executor.execute.return_value = (True, "", "")
        self.mock_clipboard_service.get_from_clipboard.return_value = (
            True,
            "受信したテキスト",
            "",
        )

        success, text, error_msg = self.service.receive_text(0.0)

        # 成功することを確認
        self.assertTrue(success)
        self.assertEqual(text, "受信したテキスト")
        self.assertEqual(error_msg, "")

        # Ctrl+A と Ctrl+C が実行されたことを確認
        self.assertEqual(self.mock_executor.execute.call_count, 2)
        self.mock_clipboard_service.get_from_clipboard.assert_called_once()

    def test_receive_text_select_all_failure(self):
        """全選択操作失敗時の処理を確認"""
        # Ctrl+Aが失敗
        self.mock_executor.execute.return_value = (False, "", "全選択エラー")

        success, text, error_msg = self.service.receive_text(0.0)

        # 失敗することを確認
        self.assertFalse(success)
        self.assertEqual(text, "")
        self.assertIn("全選択操作に失敗", error_msg)

    def test_receive_text_copy_failure(self):
        """コピー操作失敗時の処理を確認"""
        # Ctrl+Aは成功、Ctrl+Cが失敗
        self.mock_executor.execute.side_effect = [
            (True, "", ""),  # Ctrl+A成功
            (False, "", "コピーエラー"),  # Ctrl+C失敗
        ]

        success, text, error_msg = self.service.receive_text(0.0)

        # 失敗することを確認
        self.assertFalse(success)
        self.assertEqual(text, "")
        self.assertIn("コピー操作に失敗", error_msg)

    def test_receive_text_clipboard_get_failure(self):
        """クリップボード取得失敗時の処理を確認"""
        # Ctrl+A, Ctrl+Cは成功、クリップボード取得が失敗
        self.mock_executor.execute.return_value = (True, "", "")
        self.mock_clipboard_service.get_from_clipboard.return_value = (
            False,
            "",
            "クリップボード取得エラー",
        )

        success, text, error_msg = self.service.receive_text(0.0)

        # 失敗することを確認
        self.assertFalse(success)
        self.assertEqual(text, "")
        self.assertIn("クリップボード取得エラー", error_msg)


if __name__ == "__main__":
    unittest.main()
