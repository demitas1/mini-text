"""GTK4設定ダイアログ"""

from pathlib import Path
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from mini_text.config.config_manager import ConfigManager


@Gtk.Template(filename=str(Path(__file__).parent / "resources" / "settings_dialog.ui"))
class SettingsDialog(Gtk.Dialog):
    """設定ダイアログ"""

    __gtype_name__ = "SettingsDialog"

    # UIエレメント（.uiファイルからバインド）
    window_activate_spin = Gtk.Template.Child()
    key_input_spin = Gtk.Template.Child()
    copyfrom_spin = Gtk.Template.Child()
    ok_button = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()

    def __init__(self, parent, config_manager: ConfigManager, **kwargs):
        """
        Args:
            parent: 親ウィンドウ
            config_manager: 設定管理
        """
        super().__init__(transient_for=parent, **kwargs)

        self.config_manager = config_manager

        # 現在の設定値を読み込んで表示
        self.load_settings()

        # シグナル接続
        self.connect_signals()

    def load_settings(self):
        """現在の設定値をUIに反映"""
        window_activate_wait = self.config_manager.get_timing("window_activate_wait")
        key_input_wait = self.config_manager.get_timing("key_input_wait")
        copyfrom_wait = self.config_manager.get_timing("copyfrom_wait")

        self.window_activate_spin.set_value(window_activate_wait)
        self.key_input_spin.set_value(key_input_wait)
        self.copyfrom_spin.set_value(copyfrom_wait)

    def save_settings(self):
        """UIの値を設定に保存"""
        window_activate_wait = self.window_activate_spin.get_value()
        key_input_wait = self.key_input_spin.get_value()
        copyfrom_wait = self.copyfrom_spin.get_value()

        self.config_manager.set_timing("window_activate_wait", window_activate_wait)
        self.config_manager.set_timing("key_input_wait", key_input_wait)
        self.config_manager.set_timing("copyfrom_wait", copyfrom_wait)

        # ファイルに保存
        self.config_manager.save_config()

    def connect_signals(self):
        """シグナルとハンドラを接続"""
        self.ok_button.connect("clicked", self.on_ok_clicked)
        self.cancel_button.connect("clicked", self.on_cancel_clicked)

    def on_ok_clicked(self, button):
        """OKボタンクリック時の処理"""
        self.save_settings()
        self.close()

    def on_cancel_clicked(self, button):
        """キャンセルボタンクリック時の処理"""
        self.close()
