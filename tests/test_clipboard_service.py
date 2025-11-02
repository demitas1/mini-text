"""ClipboardServiceのユニットテスト"""

import unittest
from unittest.mock import Mock
from mini_text.services.clipboard_service import ClipboardService


class TestClipboardService(unittest.TestCase):
    """ClipboardServiceのテストケース"""

    def setUp(self):
        """各テストの前に実行される準備処理"""
        # モックのExecutorを作成
        self.mock_executor = Mock()
        self.service = ClipboardService(self.mock_executor)

    def test_copy_to_clipboard_success(self):
        """クリップボードへのコピーが成功することを確認"""
        # xclipコマンドが成功
        self.mock_executor.execute.return_value = (True, "", "")

        success, error_msg = self.service.copy_to_clipboard("テストテキスト")

        # 成功することを確認
        self.assertTrue(success)
        self.assertEqual(error_msg, "")

        # 正しいコマンドが実行されたことを確認
        self.mock_executor.execute.assert_called_once_with(
            ["xclip", "-selection", "clipboard"], input_data="テストテキスト"
        )

    def test_copy_to_clipboard_failure(self):
        """クリップボードへのコピーが失敗した場合の処理を確認"""
        # xclipコマンドが失敗
        self.mock_executor.execute.return_value = (False, "", "xclipエラー")

        success, error_msg = self.service.copy_to_clipboard("テストテキスト")

        # 失敗することを確認
        self.assertFalse(success)
        self.assertIn("コピーに失敗", error_msg)

    def test_get_from_clipboard_success(self):
        """クリップボードからの取得が成功することを確認"""
        # xclipコマンドが成功
        self.mock_executor.execute.return_value = (True, "取得したテキスト", "")

        success, text, error_msg = self.service.get_from_clipboard()

        # 成功することを確認
        self.assertTrue(success)
        self.assertEqual(text, "取得したテキスト")
        self.assertEqual(error_msg, "")

        # 正しいコマンドが実行されたことを確認
        self.mock_executor.execute.assert_called_once_with(
            ["xclip", "-selection", "clipboard", "-o"]
        )

    def test_get_from_clipboard_failure(self):
        """クリップボードからの取得が失敗した場合の処理を確認"""
        # xclipコマンドが失敗
        self.mock_executor.execute.return_value = (False, "", "xclipエラー")

        success, text, error_msg = self.service.get_from_clipboard()

        # 失敗することを確認
        self.assertFalse(success)
        self.assertEqual(text, "")
        self.assertIn("取得に失敗", error_msg)

    def test_copy_empty_string(self):
        """空文字列のコピーが正常に処理されることを確認"""
        # xclipコマンドが成功
        self.mock_executor.execute.return_value = (True, "", "")

        success, error_msg = self.service.copy_to_clipboard("")

        # 成功することを確認
        self.assertTrue(success)

        # 空文字列でコマンドが実行されたことを確認
        self.mock_executor.execute.assert_called_once_with(
            ["xclip", "-selection", "clipboard"], input_data=""
        )


if __name__ == "__main__":
    unittest.main()
