#!/usr/bin/env python3
"""IMプラグインのデバッグスクリプト"""

import sys
import os

# 環境変数を設定
os.environ["QT_IM_MODULE"] = "fcitx5"
os.environ["QT_PLUGIN_PATH"] = "/usr/lib/x86_64-linux-gnu/qt6/plugins"
os.environ["QT_DEBUG_PLUGINS"] = "1"  # プラグインロードのデバッグ情報を表示

from PyQt6.QtWidgets import QApplication, QPlainTextEdit

app = QApplication(sys.argv)

# 利用可能なIMを確認
print("=== 利用可能な入力メソッド ===")
from PyQt6.QtGui import QInputMethod
print(f"QInputMethod available: {QInputMethod}")

# テスト用ウィジェット
text_edit = QPlainTextEdit()
text_edit.setPlaceholderText("ここで日本語入力をテスト...")
text_edit.resize(400, 300)
text_edit.show()

print("\n=== QT_PLUGIN_PATH ===")
print(os.environ.get("QT_PLUGIN_PATH"))

print("\n=== QT_IM_MODULE ===")
print(os.environ.get("QT_IM_MODULE"))

sys.exit(app.exec())
