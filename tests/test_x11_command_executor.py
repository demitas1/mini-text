"""X11CommandExecutorのユニットテスト"""

import unittest
from mini_text.utils.x11_command_executor import X11CommandExecutor


class TestX11CommandExecutor(unittest.TestCase):
    """X11CommandExecutorのテストケース"""

    def test_execute_simple_command(self):
        """単純なコマンド実行が成功することを確認"""
        success, stdout, stderr = X11CommandExecutor.execute(["echo", "test"])

        self.assertTrue(success, "echoコマンドは成功すべき")
        self.assertIn("test", stdout, "stdoutにtestが含まれるべき")
        self.assertEqual(stderr, "", "stderrは空であるべき")

    def test_execute_with_input_data(self):
        """標準入力を使用したコマンド実行が成功することを確認"""
        # catコマンドで標準入力をそのまま出力
        success, stdout, stderr = X11CommandExecutor.execute(["cat"], input_data="テスト入力")

        self.assertTrue(success, "catコマンドは成功すべき")
        self.assertIn("テスト入力", stdout, "stdoutに入力データが含まれるべき")

    def test_execute_nonexistent_command(self):
        """存在しないコマンドの実行が適切に失敗することを確認"""
        success, stdout, stderr = X11CommandExecutor.execute(["nonexistent_command_12345"])

        self.assertFalse(success, "存在しないコマンドは失敗すべき")
        self.assertIn("見つかりません", stderr, "エラーメッセージに'見つかりません'が含まれるべき")

    def test_execute_command_with_error(self):
        """エラーを返すコマンドが適切に処理されることを確認"""
        # ls で存在しないディレクトリを指定
        success, stdout, stderr = X11CommandExecutor.execute(
            ["ls", "/nonexistent_directory_12345"]
        )

        self.assertFalse(success, "エラーコマンドは失敗すべき")
        self.assertNotEqual(stderr, "", "stderrにエラーメッセージが含まれるべき")

    def test_return_types(self):
        """戻り値の型が正しいことを確認"""
        success, stdout, stderr = X11CommandExecutor.execute(["echo", "test"])

        self.assertIsInstance(success, bool)
        self.assertIsInstance(stdout, str)
        self.assertIsInstance(stderr, str)


if __name__ == "__main__":
    unittest.main()
