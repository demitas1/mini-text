"""ConfigManagerのユニットテスト"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from mini_text.config.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """ConfigManagerのテストケース"""

    def setUp(self):
        """各テストの前に実行される準備処理"""
        # 一時ディレクトリを作成
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")

    def tearDown(self):
        """各テストの後に実行されるクリーンアップ処理"""
        # 一時ディレクトリを削除
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_default_config(self):
        """デフォルト設定が正しく読み込まれることを確認"""
        config = ConfigManager(self.config_path)

        width, height = config.get_window_size()
        self.assertEqual(width, 800)
        self.assertEqual(height, 600)

        window_activate_wait = config.get_timing("window_activate_wait")
        self.assertEqual(window_activate_wait, 0.3)

        key_input_wait = config.get_timing("key_input_wait")
        self.assertEqual(key_input_wait, 0.3)

        copyfrom_wait = config.get_timing("copyfrom_wait")
        self.assertEqual(copyfrom_wait, 3.0)

    def test_save_and_load_config(self):
        """設定の保存と読み込みが正しく動作することを確認"""
        # 設定を変更して保存
        config1 = ConfigManager(self.config_path)
        config1.set_window_size(1024, 768)
        config1.set_timing("copyfrom_wait", 5.0)
        config1.save_config()

        # ファイルが作成されたことを確認
        self.assertTrue(os.path.exists(self.config_path))

        # 新しいインスタンスで読み込み
        config2 = ConfigManager(self.config_path)
        width, height = config2.get_window_size()
        copyfrom_wait = config2.get_timing("copyfrom_wait")

        self.assertEqual(width, 1024)
        self.assertEqual(height, 768)
        self.assertEqual(copyfrom_wait, 5.0)

    def test_config_directory_creation(self):
        """設定ディレクトリが自動作成されることを確認"""
        # 深い階層のパスを作成
        deep_path = os.path.join(self.temp_dir, "level1", "level2", "config.json")

        config = ConfigManager(deep_path)
        config.save_config()

        # ファイルが作成されたことを確認
        self.assertTrue(os.path.exists(deep_path))

    def test_get_all_config(self):
        """全設定の取得が正しく動作することを確認"""
        config = ConfigManager(self.config_path)
        all_config = config.get_all_config()

        self.assertIsInstance(all_config, dict)
        self.assertIn("window", all_config)
        self.assertIn("timing", all_config)
        self.assertIn("width", all_config["window"])
        self.assertIn("height", all_config["window"])

    def test_invalid_json_handling(self):
        """不正なJSONファイルの処理を確認"""
        # 不正なJSONファイルを作成
        with open(self.config_path, "w") as f:
            f.write("{ invalid json }")

        # デフォルト値で読み込まれることを確認
        config = ConfigManager(self.config_path)
        width, height = config.get_window_size()
        self.assertEqual(width, 800)
        self.assertEqual(height, 600)

    def test_partial_config_loading(self):
        """部分的な設定ファイルの読み込みを確認"""
        # window設定のみ含むファイルを作成
        partial_config = {"window": {"width": 1280, "height": 720}}

        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(partial_config, f)

        config = ConfigManager(self.config_path)

        # window設定は読み込まれる
        width, height = config.get_window_size()
        self.assertEqual(width, 1280)
        self.assertEqual(height, 720)

        # timing設定はデフォルト値が使用される
        copyfrom_wait = config.get_timing("copyfrom_wait")
        self.assertEqual(copyfrom_wait, 3.0)

    def test_default_config_path(self):
        """デフォルト設定パスが正しく生成されることを確認"""
        config = ConfigManager()

        expected_path = str(Path.home() / ".config" / "mini-text" / "config.json")
        self.assertEqual(config.config_path, expected_path)


if __name__ == "__main__":
    unittest.main()
