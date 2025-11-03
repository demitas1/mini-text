"""DependencyCheckerのユニットテスト"""

import unittest
from mini_text.utils.dependency_checker import DependencyChecker


class TestDependencyChecker(unittest.TestCase):
    """DependencyCheckerのテストケース"""

    def test_check_dependencies(self):
        """依存関係チェックが動作することを確認"""
        all_available, missing = DependencyChecker.check_dependencies()

        # 戻り値の型を確認
        self.assertIsInstance(all_available, bool)
        self.assertIsInstance(missing, list)

        # missingリストの要素が文字列であることを確認
        for tool in missing:
            self.assertIsInstance(tool, str)

        # all_availableとmissingの整合性を確認
        if all_available:
            self.assertEqual(len(missing), 0, "all_availableがTrueの場合、missingは空であるべき")
        else:
            self.assertGreater(
                len(missing), 0, "all_availableがFalseの場合、missingに要素があるべき"
            )

    def test_required_commands_defined(self):
        """必要なコマンドリストが定義されていることを確認"""
        self.assertTrue(hasattr(DependencyChecker, "REQUIRED_COMMANDS"))
        self.assertIsInstance(DependencyChecker.REQUIRED_COMMANDS, list)
        self.assertGreater(len(DependencyChecker.REQUIRED_COMMANDS), 0)


if __name__ == "__main__":
    unittest.main()
