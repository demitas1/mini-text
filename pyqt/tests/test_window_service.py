"""WindowServiceのユニットテスト"""

import unittest
from unittest.mock import Mock
from mini_text.services.window_service import WindowService


class TestWindowService(unittest.TestCase):
    """WindowServiceのテストケース"""

    def setUp(self):
        """各テストの前に実行される準備処理"""
        # モックのExecutorを作成
        self.mock_executor = Mock()
        self.service = WindowService(self.mock_executor)

    def test_get_window_list_success(self):
        """ウィンドウ一覧取得が成功することを確認"""
        # モックの戻り値を設定
        # xdotool search の戻り値
        self.mock_executor.execute.side_effect = [
            (True, "12345\n67890\n", ""),  # search結果
            (True, "テストウィンドウ1", ""),  # getwindowname for 12345
            (True, "テストウィンドウ2", ""),  # getwindowname for 67890
        ]

        result = self.service.get_window_list()

        # 結果を検証
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("12345", "テストウィンドウ1"))
        self.assertEqual(result[1], ("67890", "テストウィンドウ2"))

    def test_get_window_list_search_failure(self):
        """ウィンドウ検索が失敗した場合の処理を確認"""
        # search コマンドが失敗
        self.mock_executor.execute.return_value = (False, "", "エラー")

        result = self.service.get_window_list()

        # 空のリストが返されることを確認
        self.assertEqual(result, [])

    def test_get_window_list_empty(self):
        """ウィンドウが存在しない場合の処理を確認"""
        # searchは成功するが結果が空
        self.mock_executor.execute.return_value = (True, "", "")

        result = self.service.get_window_list()

        # 空のリストが返されることを確認
        self.assertEqual(result, [])

    def test_activate_window_success(self):
        """ウィンドウアクティベートが成功することを確認"""
        # windowactivateが成功
        self.mock_executor.execute.return_value = (True, "", "")

        success, error_msg = self.service.activate_window("12345", 0.0)

        # 成功することを確認
        self.assertTrue(success)
        self.assertEqual(error_msg, "")

        # 正しいコマンドが実行されたことを確認
        self.mock_executor.execute.assert_called_once_with(
            ["xdotool", "windowactivate", "--sync", "12345"]
        )

    def test_activate_window_failure(self):
        """ウィンドウアクティベートが失敗した場合の処理を確認"""
        # windowactivateが失敗
        self.mock_executor.execute.return_value = (False, "", "ウィンドウが見つかりません")

        success, error_msg = self.service.activate_window("99999", 0.0)

        # 失敗することを確認
        self.assertFalse(success)
        self.assertIn("アクティブ化に失敗", error_msg)


if __name__ == "__main__":
    unittest.main()
