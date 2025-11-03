"""ConfigManagerのpytestテスト"""

import pytest
import json
from pathlib import Path
from mini_text.config.config_manager import ConfigManager


def test_default_config(temp_config_file):
    """デフォルト設定が正しく読み込まれることを確認"""
    config = ConfigManager(temp_config_file)

    width, height = config.get_window_size()
    assert width == 800
    assert height == 600

    window_activate_wait = config.get_timing("window_activate_wait")
    assert window_activate_wait == 0.3

    key_input_wait = config.get_timing("key_input_wait")
    assert key_input_wait == 0.3

    copyfrom_wait = config.get_timing("copyfrom_wait")
    assert copyfrom_wait == 3.0


def test_save_and_load_config(temp_config_file):
    """設定の保存と読み込みが正しく動作することを確認"""
    # 設定を変更して保存
    config1 = ConfigManager(temp_config_file)
    config1.set_window_size(1024, 768)
    config1.set_timing("copyfrom_wait", 5.0)
    config1.save_config()

    # ファイルが作成されたことを確認
    assert Path(temp_config_file).exists()

    # 新しいインスタンスで読み込み
    config2 = ConfigManager(temp_config_file)
    width, height = config2.get_window_size()
    copyfrom_wait = config2.get_timing("copyfrom_wait")

    assert width == 1024
    assert height == 768
    assert copyfrom_wait == 5.0


def test_config_directory_creation(tmp_path):
    """設定ディレクトリが自動作成されることを確認"""
    # 深い階層のパスを作成
    deep_path = tmp_path / "level1" / "level2" / "config.json"

    config = ConfigManager(str(deep_path))
    config.save_config()

    # ファイルが作成されたことを確認
    assert deep_path.exists()


def test_get_all_config(temp_config_file):
    """全設定の取得が正しく動作することを確認"""
    config = ConfigManager(temp_config_file)
    all_config = config.get_all_config()

    assert isinstance(all_config, dict)
    assert "window" in all_config
    assert "timing" in all_config
    assert "width" in all_config["window"]
    assert "height" in all_config["window"]


def test_invalid_json_handling(temp_config_file):
    """不正なJSONファイルの処理を確認"""
    # 不正なJSONファイルを作成
    with open(temp_config_file, "w") as f:
        f.write("{ invalid json }")

    # デフォルト値で読み込まれることを確認
    config = ConfigManager(temp_config_file)
    width, height = config.get_window_size()
    assert width == 800
    assert height == 600


def test_partial_config_loading(temp_config_file):
    """部分的な設定ファイルの読み込みを確認"""
    # window設定のみ含むファイルを作成
    partial_config = {"window": {"width": 1280, "height": 720}}

    with open(temp_config_file, "w", encoding="utf-8") as f:
        json.dump(partial_config, f)

    config = ConfigManager(temp_config_file)

    # window設定は読み込まれる
    width, height = config.get_window_size()
    assert width == 1280
    assert height == 720

    # timing設定はデフォルト値が使用される
    copyfrom_wait = config.get_timing("copyfrom_wait")
    assert copyfrom_wait == 3.0


def test_default_config_path():
    """デフォルト設定パスが正しく生成されることを確認"""
    config = ConfigManager()

    expected_path = str(Path.home() / ".config" / "mini-text" / "config.json")
    assert config.config_path == expected_path
