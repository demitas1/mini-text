"""pytest設定ファイル"""

import pytest
from pathlib import Path


@pytest.fixture
def temp_config_file(tmp_path):
    """一時設定ファイルのフィクスチャ"""
    config_file = tmp_path / "config.json"
    return str(config_file)


@pytest.fixture
def temp_config_dir(tmp_path):
    """一時設定ディレクトリのフィクスチャ"""
    config_dir = tmp_path / "mini-text"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir
