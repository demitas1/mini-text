# GTK4実装 動作確認手順

**最終更新**: 2025-11-03
**ステータス**: Phase 3完了、動作確認済み ✓

## 前提条件

- xdotoolがインストール済み（xclipは不要）
- X11デスクトップ環境で実行
- システムにpython3-gi, gir1.2-gtk-4.0がインストール済み
- venvは`--system-site-packages`で作成

## 実行方法

```bash
# 仮想環境をアクティベート
cd gtk4
source venv/bin/activate

# アプリケーションを起動
python main.py
```

## 確認項目

### 基本動作
- [x] アプリケーションが起動する
- [x] ウィンドウが常に最前面に表示される（GTK4の制限あり）
- [x] ウィンドウサイズがデフォルト800x600である

### ウィンドウリスト
- [x] 起動時に自動的にウィンドウリストが表示される
- [x] リフレッシュボタンでウィンドウリストが更新される
- [x] ウィンドウリストに "ID: ウィンドウ名" の形式で表示される

### テキスト送信機能
1. [x] ウィンドウリストから送信先を選択
2. [x] テキストボックスにテキストを入力（日本語含む）
3. [x] 送信ボタンをクリック
4. [x] 選択したウィンドウにテキストが送信される
5. [x] ステータスバーに「テキストを送信しました」と表示される

**動作確認済み**: Inkscapeで正常に動作

### IME/日本語入力テスト ✓
- [x] テキストボックスで日本語入力ができる（fcitx5/mozc）
- [x] 日本語テキストを他のウィンドウに送信できる
- [x] 他のウィンドウから日本語テキストをコピーできる

**重要**: PyQt6実装で失敗していたIME統合がGTK4で成功！

### テキストコピー機能
1. [x] コピーボタンをクリック
2. [x] ステータスバーに「X秒後にコピーを開始します...」と表示される
3. [x] 指定時間内にコピー元のテキストボックスをクリック
4. [x] テキストが自動的にコピーされる
5. [x] mini-textのテキストボックスにコピーしたテキストが表示される
6. [x] ステータスバーに「テキストをコピーしました」と表示される

**動作確認済み**: Inkscapeで正常に動作

### エラーハンドリング
- [x] ウィンドウ未選択で送信: 「ウィンドウを選択してください」エラー表示
- [x] テキスト未入力で送信: 「送信するテキストを入力してください」エラー表示
- [x] エラーメッセージがステータスバーに表示される（赤文字）

### メニュー
- [x] メニューボタンが表示される
- [x] 設定メニューをクリック: 「Phase 4で実装されます」ダイアログ表示
- [x] 終了メニューでアプリケーションが終了する

### ウィンドウサイズ保存
1. [x] ウィンドウサイズを変更
2. [x] アプリケーションを終了
3. [x] 再度起動
4. [x] 前回のウィンドウサイズが復元される

## トラブルシューティング

### アプリケーションが起動しない

```bash
# 依存関係を確認
source venv/bin/activate
python -c "from mini_text.utils.dependency_checker import DependencyChecker; print(DependencyChecker.check_dependencies())"
```

### PyGObjectが見つからない

システムパッケージがインストールされているか確認:
```bash
python3 -c "import gi; print('PyGObject version:', gi.__version__)"
```

venvが`--system-site-packages`で作成されているか確認:
```bash
cat venv/pyvenv.cfg | grep system-site-packages
# include-system-site-packages = true であること
```

### UIファイルが見つからない

```bash
# UIファイルの存在を確認
ls -la mini_text/ui/resources/main_window.ui
```

### モジュールインポートエラー

```bash
# Pythonパスを確認
source venv/bin/activate
python -c "import sys; print('\n'.join(sys.path))"
```

## 既知の制限事項

- 設定機能はPhase 4で実装予定
- 設定ダイアログは未実装
- 常に最前面表示はGTK4の制限により完全には動作しない

## Phase 3で解決した問題

### GTK4ネイティブクリップボードAPIへの移行
**背景**: 従来はxclipコマンドを使用していたが、外部依存を削減するためGTK4の`Gdk.Clipboard` APIに移行

**実装内容**:
1. `GtkClipboardService`を新規作成
2. 書き込み: `clipboard.set(text)` - 同期的に即座に完了
3. 読み込み: `clipboard.read_text_async()` - 非同期APIを同期的にラップ
   - `GLib.MainContext.pending()`でイベント処理
   - タイムアウト5秒で安全に待機

**影響ファイル**:
- `mini_text/services/gtk_clipboard_service.py` (新規)
- `main.py` (GtkClipboardServiceを注入)

**メリット**:
- xclip依存の削除
- プロセス管理の簡素化
- GTKネイティブ統合

### 過去の問題（xclip使用時）
**症状**: テキスト送信時に「クリップボードへのコピーに失敗しました: コマンドがタイムアウトしました」エラー

**原因**: xclipはクリップボード所有権を保持し続けるためプロセスが終了せず、`subprocess.run()`が待機し続ける

**旧解決策**: `subprocess.Popen()`でバックグラウンド起動（現在はGTK4 APIを使用）

## PyQt6実装との違い

### 解決された問題 ✓
- **IME統合**: GTK4はfcitx5/mozcと安定して統合できる
- **日本語入力**: PyQt6で発生していた問題が解決
- **クリップボード操作**: GTK4ネイティブAPIで安定動作（xclip不要）

### 動作の違い
- メニューバーの代わりにメニューボタンを使用
- ウィジェットの見た目がGTK4スタイル
