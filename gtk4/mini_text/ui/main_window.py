"""GTK4メインウィンドウ"""

import time
from pathlib import Path
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

from mini_text.services.window_service import WindowService
from mini_text.services.text_service import TextService
from mini_text.config.config_manager import ConfigManager


@Gtk.Template(filename=str(Path(__file__).parent / "resources" / "main_window.ui"))
class MainWindow(Gtk.ApplicationWindow):
    """メインウィンドウ"""

    __gtype_name__ = 'MainWindow'

    # UIエレメント（.uiファイルからバインド）
    window_list = Gtk.Template.Child()
    text_view = Gtk.Template.Child()
    send_button = Gtk.Template.Child()
    copy_button = Gtk.Template.Child()
    refresh_button = Gtk.Template.Child()
    status_label = Gtk.Template.Child()

    def __init__(
        self,
        application,
        text_service: TextService,
        window_service: WindowService,
        config_manager: ConfigManager,
        **kwargs
    ):
        """
        Args:
            application: Gtk.Application
            text_service: テキスト送受信サービス
            window_service: ウィンドウ操作サービス
            config_manager: 設定管理
        """
        super().__init__(application=application, **kwargs)

        self.text_service = text_service
        self.window_service = window_service
        self.config_manager = config_manager

        # テキストバッファを取得
        self.text_buffer = self.text_view.get_buffer()

        # ウィンドウサイズを復元
        width, height = self.config_manager.get_window_size()
        self.set_default_size(width, height)

        # シグナル接続
        self.connect_signals()

        # ウィンドウ表示後に常に最前面を設定
        # GTK4では realize シグナルの後に設定する必要がある
        self.connect('realize', self._on_realize)

        # CSSでエラー表示用のスタイルを追加
        self.setup_css()

        # 初回のウィンドウリスト取得
        self.refresh_window_list()

    def setup_css(self):
        """CSSスタイルを設定"""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            .error {
                color: red;
            }
        """)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _on_realize(self, widget):
        """ウィンドウ実現時の処理 - 常に最前面を設定"""
        # GTK4ではネイティブウィンドウを取得してヒントを設定
        surface = self.get_surface()
        if surface:
            # GDK Surfaceを使用して常に最前面に設定を試みる
            # 注: GTK4では直接的な set_keep_above がないため、
            # ウィンドウマネージャー依存の動作になる
            try:
                # Waylandでは動作しない可能性がある
                from gi.repository import Gdk
                # X11の場合はウィンドウマネージャーヒントで設定
                pass  # GTK4では制限された機能
            except:
                pass

    def connect_signals(self):
        """シグナルとハンドラを接続"""
        self.refresh_button.connect('clicked', self.on_refresh_clicked)
        self.send_button.connect('clicked', self.on_send_clicked)
        self.copy_button.connect('clicked', self.on_copy_clicked)
        self.connect('close-request', self.on_close_request)

    def refresh_window_list(self):
        """ウィンドウ一覧を更新"""
        # ListBoxをクリア
        while True:
            row = self.window_list.get_row_at_index(0)
            if row is None:
                break
            self.window_list.remove(row)

        # ウィンドウ一覧を取得
        windows = self.window_service.get_window_list()

        # リストに追加
        for window_id, window_name in windows:
            label = Gtk.Label(label=f"{window_id}: {window_name}")
            label.set_halign(Gtk.Align.START)
            label.set_margin_start(6)
            label.set_margin_end(6)
            label.set_margin_top(3)
            label.set_margin_bottom(3)
            self.window_list.append(label)

        self.show_status(f"ウィンドウリストを更新しました ({len(windows)}件)")

    def on_refresh_clicked(self, button):
        """リフレッシュボタンクリック時の処理"""
        self.refresh_window_list()

    def on_send_clicked(self, button):
        """送信ボタンクリック時の処理"""
        # 選択されているウィンドウを取得
        selected_row = self.window_list.get_selected_row()
        if not selected_row:
            self.show_status("ウィンドウを選択してください", is_error=True)
            return

        # テキストを取得
        start_iter = self.text_buffer.get_start_iter()
        end_iter = self.text_buffer.get_end_iter()
        text = self.text_buffer.get_text(start_iter, end_iter, False)

        if not text:
            self.show_status("送信するテキストを入力してください", is_error=True)
            return

        # ウィンドウIDを取得
        label = selected_row.get_child()
        window_id = label.get_label().split(":")[0]

        # 設定から待機時間を取得
        activate_wait = self.config_manager.get_timing("window_activate_wait")
        key_wait = self.config_manager.get_timing("key_input_wait")

        # テキストを送信
        success, error_msg = self.text_service.send_text(
            window_id, text, activate_wait, key_wait
        )

        if success:
            self.show_status("テキストを送信しました")
        else:
            self.show_status(f"エラー: {error_msg}", is_error=True)

    def on_copy_clicked(self, button):
        """コピーボタンクリック時の処理"""
        # 設定から待機時間を取得
        copyfrom_wait = self.config_manager.get_timing("copyfrom_wait")
        key_wait = self.config_manager.get_timing("key_input_wait")

        # ユーザーに通知
        self.show_status(
            f"{copyfrom_wait}秒後にコピーを開始します。対象のテキストボックスをクリックしてください"
        )

        # GLibのタイムアウトを使用して非同期実行
        GLib.timeout_add_seconds(int(copyfrom_wait), self._do_copy, key_wait)

    def _do_copy(self, key_wait):
        """コピー実行（タイムアウトコールバック）"""
        # テキストを取得
        success, text, error_msg = self.text_service.receive_text(key_wait)

        if success:
            # テキストバッファに設定
            self.text_buffer.set_text(text)
            self.show_status("テキストをコピーしました")
        else:
            self.show_status(f"エラー: {error_msg}", is_error=True)

        return False  # タイムアウトを一回限りにする

    def show_status(self, message: str, is_error: bool = False):
        """ステータスメッセージを表示"""
        self.status_label.set_label(message)

        # エラーの場合は色を変更
        if is_error:
            self.status_label.add_css_class('error')
        else:
            self.status_label.remove_css_class('error')

    def on_close_request(self, window):
        """ウィンドウクローズ時の処理"""
        # ウィンドウサイズを保存
        width = self.get_width()
        height = self.get_height()
        self.config_manager.set_window_size(width, height)
        self.config_manager.save_config()

        return False  # クローズを許可
