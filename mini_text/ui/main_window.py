"""メインウィンドウ"""

import os
import time
from pathlib import Path
from PyQt6 import QtCore, uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import Qt

from mini_text.services.window_service import WindowService
from mini_text.services.text_service import TextService
from mini_text.config.config_manager import ConfigManager


class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(
        self,
        text_service: TextService,
        window_service: WindowService,
        config_manager: ConfigManager,
    ):
        """
        Args:
            text_service: テキスト送受信サービス
            window_service: ウィンドウ操作サービス
            config_manager: 設定管理
        """
        super().__init__()

        self.text_service = text_service
        self.window_service = window_service
        self.config_manager = config_manager

        # UIをセットアップ
        self.setup_ui()

        # ウィンドウサイズを復元
        width, height = self.config_manager.get_window_size()
        self.resize(width, height)

        # 初回のウィンドウリスト取得
        self.refresh_window_list()

    def setup_ui(self) -> None:
        """
        UIをセットアップ
        - .uiファイルをロード
        - シグナルとスロットを接続
        - 常に最前面フラグを設定
        """
        # .uiファイルのパスを取得
        ui_file = Path(__file__).parent / "resources" / "main_window.ui"

        # UIをロード
        uic.loadUi(ui_file, self)

        # 常に最前面に設定
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        # シグナルとスロットを接続
        self.refresh_button.clicked.connect(self.on_refresh_clicked)
        self.send_button.clicked.connect(self.on_send_clicked)
        self.copy_button.clicked.connect(self.on_copy_clicked)

        # メニューアクションを接続
        self.action_settings.triggered.connect(self.on_settings_clicked)
        self.action_quit.triggered.connect(self.close)

    def refresh_window_list(self) -> None:
        """ウィンドウ一覧を更新"""
        # リストをクリア
        self.window_list.clear()

        # ウィンドウ一覧を取得
        windows = self.window_service.get_window_list()

        # リストに追加
        for window_id, window_name in windows:
            # 表示形式: "ID: 名前"
            display_text = f"{window_id}: {window_name}"
            self.window_list.addItem(display_text)

        # ステータスバーに表示
        self.show_status(f"ウィンドウリストを更新しました ({len(windows)}件)")

    def on_refresh_clicked(self) -> None:
        """リフレッシュボタンクリック時の処理"""
        self.refresh_window_list()

    def on_send_clicked(self) -> None:
        """送信ボタンクリック時の処理"""
        # ウィンドウが選択されているか確認
        current_item = self.window_list.currentItem()
        if not current_item:
            self.show_status("ウィンドウを選択してください", is_error=True)
            return

        # テキストが入力されているか確認
        text = self.text_edit.toPlainText()
        if not text:
            self.show_status("送信するテキストを入力してください", is_error=True)
            return

        # ウィンドウIDを取得 (表示形式: "ID: 名前" から IDを抽出)
        window_id = current_item.text().split(":")[0]

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

    def on_copy_clicked(self) -> None:
        """コピーボタンクリック時の処理"""
        # 設定から待機時間を取得
        copyfrom_wait = self.config_manager.get_timing("copyfrom_wait")
        key_wait = self.config_manager.get_timing("key_input_wait")

        # ユーザーに通知
        self.show_status(
            f"{copyfrom_wait}秒後にコピーを開始します。対象のテキストボックスをクリックしてください"
        )

        # GUIを更新してメッセージを表示
        QtCore.QCoreApplication.processEvents()

        # 待機
        time.sleep(copyfrom_wait)

        # テキストを取得
        success, text, error_msg = self.text_service.receive_text(key_wait)

        if success:
            # テキストボックスに表示
            self.text_edit.setPlainText(text)
            self.show_status("テキストをコピーしました")
        else:
            self.show_status(f"エラー: {error_msg}", is_error=True)

    def on_settings_clicked(self) -> None:
        """設定メニュークリック時の処理"""
        # Phase 4で実装
        QMessageBox.information(
            self, "情報", "設定機能はPhase 4で実装されます"
        )

    def show_status(self, message: str, is_error: bool = False) -> None:
        """
        ステータスバーにメッセージを表示

        Args:
            message: 表示するメッセージ
            is_error: エラーメッセージの場合True
        """
        self.statusbar.showMessage(message)

        # エラーの場合は色を変更（オプション）
        if is_error:
            self.statusbar.setStyleSheet("color: red;")
        else:
            self.statusbar.setStyleSheet("")

    def closeEvent(self, event) -> None:
        """
        ウィンドウクローズ時の処理
        ウィンドウサイズを保存
        """
        # ウィンドウサイズを保存
        self.config_manager.set_window_size(self.width(), self.height())
        self.config_manager.save_config()

        # イベントを受け入れる
        event.accept()
