#!/usr/bin/env python3
"""mini-text GTK4アプリケーションのエントリーポイント"""

import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, Gio

from mini_text.utils.dependency_checker import DependencyChecker
from mini_text.utils.x11_command_executor import X11CommandExecutor
from mini_text.config.config_manager import ConfigManager
from mini_text.services.window_service import WindowService
from mini_text.services.gtk_clipboard_service import GtkClipboardService
from mini_text.services.text_service import TextService
from mini_text.ui.main_window import MainWindow
from mini_text.ui.settings_dialog import SettingsDialog


class MiniTextApplication(Gtk.Application):
    """mini-textアプリケーション"""

    def __init__(self):
        super().__init__(
            application_id='com.example.minitext',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        # サービスの初期化
        self.config_manager = None
        self.text_service = None
        self.window_service = None
        self.main_window = None

    def do_startup(self):
        """アプリケーション起動時の初期化"""
        Gtk.Application.do_startup(self)

        # アクションを設定
        settings_action = Gio.SimpleAction.new("settings", None)
        settings_action.connect("activate", self.on_settings_action)
        self.add_action(settings_action)

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_action)
        self.add_action(quit_action)

        # 設定マネージャーを初期化
        self.config_manager = ConfigManager()

        # X11コマンド実行ユーティリティを作成
        executor = X11CommandExecutor()

        # サービスを作成
        self.window_service = WindowService(executor)

        # GTK4 Clipboardサービスを使用
        display = Gdk.Display.get_default()
        clipboard = display.get_clipboard()
        clipboard_service = GtkClipboardService(clipboard)

        self.text_service = TextService(self.window_service, clipboard_service, executor)

    def do_activate(self):
        """アプリケーションアクティベート時の処理"""
        # メインウィンドウが既に存在する場合は前面に表示
        if self.main_window:
            self.main_window.present()
            return

        # メインウィンドウを作成
        self.main_window = MainWindow(
            application=self,
            text_service=self.text_service,
            window_service=self.window_service,
            config_manager=self.config_manager
        )
        self.main_window.present()

    def on_settings_action(self, action, param):
        """設定アクション"""
        dialog = SettingsDialog(
            parent=self.main_window,
            config_manager=self.config_manager
        )
        dialog.present()

    def on_quit_action(self, action, param):
        """終了アクション"""
        self.quit()


def check_dependencies() -> bool:
    """
    依存関係をチェック

    Returns:
        bool: 全ての依存関係が満たされている場合True
    """
    all_available, missing = DependencyChecker.check_dependencies()

    if not all_available:
        error_message = (
            "以下のツールがインストールされていません:\n\n"
            + "\n".join(f"- {tool}" for tool in missing)
            + "\n\n以下のコマンドでインストールしてください:\n"
            + "sudo apt install " + " ".join(missing)
        )

        print("エラー: 依存関係が満たされていません")
        print(error_message)
        return False

    return True


def main():
    """メイン関数"""
    # 依存関係チェック
    if not check_dependencies():
        sys.exit(1)

    # アプリケーションを作成・実行
    app = MiniTextApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
