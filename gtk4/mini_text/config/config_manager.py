"""設定ファイル管理"""

import copy
import json
import os
from pathlib import Path
from typing import Optional


class ConfigManager:
    """設定ファイルの読み書きを管理するクラス (JSON形式)"""

    # デフォルト設定値
    DEFAULT_CONFIG = {
        "window": {"width": 800, "height": 600},
        "timing": {
            "window_activate_wait": 0.3,
            "key_input_wait": 0.3,
            "copyfrom_wait": 3.0,
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: 設定ファイルのパス (Noneの場合は $HOME/.config/mini-text/config.json)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        self.load_config()

    def _get_default_config_path(self) -> str:
        """デフォルトの設定ファイルパスを取得"""
        home = Path.home()
        config_dir = home / ".config" / "mini-text"
        return str(config_dir / "config.json")

    def _ensure_config_dir(self) -> None:
        """設定ファイルディレクトリが存在しない場合は作成"""
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> None:
        """設定ファイルを読み込む。ファイルが存在しない場合はデフォルト値を使用"""
        if not os.path.exists(self.config_path):
            # ファイルが存在しない場合はデフォルト値を使用
            self.config = copy.deepcopy(self.DEFAULT_CONFIG)
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded_config = json.load(f)

            # デフォルト設定とマージ（不足しているキーがあっても動作するように）
            self.config = copy.deepcopy(self.DEFAULT_CONFIG)
            if "window" in loaded_config:
                self.config["window"].update(loaded_config["window"])
            if "timing" in loaded_config:
                self.config["timing"].update(loaded_config["timing"])

        except (json.JSONDecodeError, IOError) as e:
            # 読み込み失敗時はデフォルト値を使用
            print(f"警告: 設定ファイルの読み込みに失敗しました: {e}")
            self.config = copy.deepcopy(self.DEFAULT_CONFIG)

    def save_config(self) -> None:
        """現在の設定をファイルに保存"""
        try:
            # ディレクトリが存在しない場合は作成
            self._ensure_config_dir()

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

        except IOError as e:
            print(f"エラー: 設定ファイルの保存に失敗しました: {e}")

    def get_window_size(self) -> tuple[int, int]:
        """ウィンドウサイズを取得"""
        return self.config["window"]["width"], self.config["window"]["height"]

    def set_window_size(self, width: int, height: int) -> None:
        """ウィンドウサイズを設定"""
        self.config["window"]["width"] = width
        self.config["window"]["height"] = height

    def get_timing(self, key: str) -> float:
        """
        指定したタイミング設定値を取得

        Args:
            key: "window_activate_wait", "key_input_wait", "copyfrom_wait"
        """
        return self.config["timing"].get(key, 0.3)

    def set_timing(self, key: str, value: float) -> None:
        """指定したタイミング設定値を設定"""
        self.config["timing"][key] = value

    def get_all_config(self) -> dict:
        """全設定を辞書で取得"""
        return self.config.copy()
