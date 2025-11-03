# IME統合の問題と調査結果

## 問題の概要

Phase 3実装後、PyQt6アプリケーションでfcitx5/mozcによる日本語入力ができない問題が発生。

## 環境情報

- OS: Ubuntu 24.04.3 LTS (Noble Numbat)
- Desktop: KDE (X11)
- IME: fcitx5 5.1.7 + mozc
- Python: 3.12
- PyQt6: 6.10.0 (pipでvenv環境にインストール)
- システムQt6プラグイン: fcitx5-frontend-qt6 5.1.4-1build5

## 実施した対策

### 1. 環境変数の設定
```python
os.environ["QT_IM_MODULE"] = "fcitx5"
os.environ["XMODIFIERS"] = "@im=fcitx5"
os.environ["GTK_IM_MODULE"] = "fcitx5"
os.environ["QT_PLUGIN_PATH"] = "/lib/x86_64-linux-gnu/qt6/plugins"
```

**結果**: 効果なし

### 2. シンボリックリンクの作成

システムのfcitx5プラグインをvenv内のPyQt6プラグインディレクトリにリンク:

```bash
ln -sf /lib/x86_64-linux-gnu/qt6/plugins/platforminputcontexts/libfcitx5platforminputcontextplugin.so \
       venv/lib/python3.12/site-packages/PyQt6/Qt6/plugins/platforminputcontexts/
```

**結果**: プラグインは検出されるが、ロードに失敗

## 根本原因

デバッグログから判明した問題:

```
qt.core.library: "/usr/lib/x86_64-linux-gnu/qt6/plugins/platforminputcontexts/libfcitx5platforminputcontextplugin.so"
cannot load: Cannot load library: undefined symbol: _ZN22QWindowSystemInterface22handleExtendedKeyEventEP7QWindowmN6QEvent4TypeEi6QFlagsIN2Qt16KeyboardModifierEEjjjRK7QStringbtb, version Qt_6_PRIVATE_API
```

### 問題の詳細

1. **バージョン不一致**
   - システムのfcitx5-frontend-qt6プラグイン: システムQt6 (Ubuntu 24.04標準) でコンパイル
   - venv内のPyQt6: pip経由でインストール (Qt 6.10.0)
   - 両者のQt6バージョンが異なり、ABIが互換性なし

2. **Qt6のプライベートAPI依存**
   - fcitx5プラグインがQt6のプライベートAPIに依存
   - プライベートAPIはバージョン間で互換性が保証されない
   - 異なるQt6バージョン間でシンボルの不一致が発生

## 解決策の選択肢

### オプションA: システムのPyQt6を使用

**方法**:
```bash
sudo apt install python3-pyqt6
# venv作成時に --system-site-packages を使用
python3 -m venv --system-site-packages venv
```

**メリット**:
- システムのQt6とfcitx5プラグインのバージョンが一致
- IMEが正常に動作する

**デメリット**:
- PyQt6のバージョンをプロジェクトで管理できない
- システムの更新に依存
- 他の依存関係もシステムと混在する可能性

### オプションB: PySide6を使用

**方法**:
```bash
pip install PySide6
```

**メリット**:
- Qtの公式Pythonバインディング
- pip経由でインストール可能
- 同様の問題が発生する可能性は低い（要検証）

**デメリット**:
- APIがPyQt6と微妙に異なる
- コードの書き換えが必要
- 同じバージョン問題が発生する可能性あり

### オプションC: Tkinterを使用

**方法**:
```bash
# 標準ライブラリなのでインストール不要
```

**メリット**:
- Python標準ライブラリ
- IME統合が安定している
- シンプルで軽量

**デメリット**:
- 現代的なUIが作りにくい
- Qt Designerのような視覚的デザインツールがない
- 既存のコード（Phase 1-3）の大幅な書き換えが必要

### オプションD: GTK4 (PyGObject)を使用

**方法**:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
```

**メリット**:
- GNOMEプロジェクトの標準UIツールキット
- IME統合が安定している
- Gladeという視覚的デザインツールがある

**デメリット**:
- 既存のコード（Phase 1-3）の大幅な書き換えが必要
- Qtに比べて学習曲線が異なる

## 推奨アプローチ

### 短期的解決策: オプションA（システムPyQt6）

Phase 3を完了させるために、まずシステムのPyQt6を使用:

1. システムPyQt6をインストール
   ```bash
   sudo apt install python3-pyqt6
   ```

2. venvを再作成
   ```bash
   deactivate
   rm -rf venv
   python3 -m venv --system-site-packages venv
   source venv/bin/activate
   ```

3. プロジェクト固有の依存関係のみインストール
   - PyQt6はシステムから利用
   - 他のパッケージは必要に応じてインストール

4. Phase 3-5を完了

### 長期的検討: 他のツールキットの評価

Phase 5完了後、以下を評価:

1. **PySide6の検証**
   - 同じ問題が発生するか確認
   - 発生しなければ移行を検討

2. **GTK4の検証**
   - プロトタイプを作成
   - IME動作を確認
   - 開発体験を評価

3. **最終判断**
   - プロジェクトの長期的な保守性
   - 開発者の慣れ
   - ユーザー体験

## 教訓

1. **venv環境でのGUIアプリケーション開発の課題**
   - システム統合（IME、テーマ等）が必要な場合、venvの隔離性が障害になる
   - 特にQt/PyQt6のようなC++バインディングは、システムライブラリとの互換性が重要

2. **プライベートAPIへの依存**
   - IMEプラグインがQt6のプライベートAPIに依存
   - バージョン管理が困難

3. **早期の環境検証の重要性**
   - IME統合のような重要機能は、Phase 1で検証すべきだった
   - プロトタイプでの動作確認が重要

## 参考情報

- fcitx5-diagnose出力: 添付済み
- Qt6プラグインパス: `/lib/x86_64-linux-gnu/qt6/plugins/platforminputcontexts/`
- システムQt6: Ubuntu 24.04標準パッケージ
- PyQt6 (pip): 6.10.0 (独自バンドルQt 6.10.0)

## ステータス

**現在**: Phase 3実装完了、IME問題により日本語入力不可

**次のアクション**: オプションA（システムPyQt6）を試すか、別のツールキットを検討
