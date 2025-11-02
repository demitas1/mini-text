#!/usr/bin/env python3
"""mini-text アプリケーションのエントリーポイント"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from mini_text.utils.dependency_checker import DependencyChecker
from mini_text.utils.x11_command_executor import X11CommandExecutor
from mini_text.config.config_manager import ConfigManager
from mini_text.services.window_service import WindowService
from mini_text.services.clipboard_service import ClipboardService
from mini_text.services.text_service import TextService
from mini_text.ui.main_window import MainWindow


def check_dependencies() -> bool:
    """
    依存関係をチェック

    Returns:
        bool: 全ての依存関係が満たされている場合True
    """
    all_available, missing = DependencyChecker.check_dependencies()

    if not all_available:
        # エラーダイアログを表示
        error_message = (
            "以下のツールがインストールされていません:\n\n"
            + "\n".join(f"- {tool}" for tool in missing)
            + "\n\n以下のコマンドでインストールしてください:\n"
            + "sudo apt install " + " ".join(missing)
        )

        # QApplicationが必要なのでここでは作成しない
        # 代わりにコンソールにエラーを出力
        print("エラー: 依存関係が満たされていません")
        print(error_message)
        return False

    return True


def main():
    """メイン関数"""
    # 依存関係チェック（Qt初期化前に実行）
    if not check_dependencies():
        sys.exit(1)

    # QApplicationを作成
    app = QApplication(sys.argv)

    # 設定マネージャーを初期化
    config_manager = ConfigManager()

    # X11コマンド実行ユーティリティを作成
    executor = X11CommandExecutor()

    # サービスを作成
    window_service = WindowService(executor)
    clipboard_service = ClipboardService(executor)
    text_service = TextService(window_service, clipboard_service, executor)

    # メインウィンドウを作成
    main_window = MainWindow(text_service, window_service, config_manager)
    main_window.show()

    # アプリケーションを実行
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
