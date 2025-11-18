#!/bin/bash
# mini-text GTK4版 実行ラッパースクリプト
#
# 使用方法:
#   ./mini-text-gtk4.sh           # アプリケーションを実行
#   ./mini-text-gtk4.sh --setup   # 環境セットアップのみ
#   ./mini-text-gtk4.sh --test    # テストを実行

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GTK4_DIR="$SCRIPT_DIR/gtk4"
VENV_DIR="$GTK4_DIR/venv"

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# システム依存関係のチェック
check_system_dependencies() {
    print_info "システム依存関係をチェック中..."

    local missing_deps=()

    # xdotoolのチェック
    if ! command -v xdotool &> /dev/null; then
        missing_deps+=("xdotool")
    fi

    # python3-giのチェック（PyGObjectモジュールで確認）
    if ! python3 -c "import gi" &> /dev/null; then
        missing_deps+=("python3-gi")
    fi

    # GTK4のチェック
    if ! python3 -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk" &> /dev/null; then
        missing_deps+=("gir1.2-gtk-4.0")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "以下のシステム依存関係が不足しています:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        echo ""
        echo "インストールコマンド:"
        echo "  sudo apt install ${missing_deps[*]}"
        return 1
    fi

    print_info "システム依存関係: OK"
    return 0
}

# venv環境のセットアップ
setup_venv() {
    print_info "Python仮想環境をセットアップ中..."

    if [ ! -d "$VENV_DIR" ]; then
        print_info "仮想環境を作成中 (--system-site-packages)..."
        cd "$GTK4_DIR"
        python3 -m venv --system-site-packages venv
    else
        print_info "仮想環境は既に存在します"
    fi

    # venvのアクティベート
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"

    # 依存関係のインストール
    print_info "Python依存関係をインストール中..."
    cd "$GTK4_DIR"
    pip install -q -r requirements.txt

    print_info "セットアップ完了"
}

# テストの実行
run_tests() {
    print_info "テストを実行中..."

    # venvのアクティベート
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"

    cd "$GTK4_DIR"
    pytest tests/ -v
}

# アプリケーションの実行
run_app() {
    print_info "mini-text GTK4版を起動中..."

    # venvのアクティベート
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"

    cd "$GTK4_DIR"
    python main.py
}

# メイン処理
main() {
    print_info "mini-text GTK4版 実行ラッパー"
    echo ""

    # gtk4ディレクトリの存在確認
    if [ ! -d "$GTK4_DIR" ]; then
        print_error "gtk4ディレクトリが見つかりません: $GTK4_DIR"
        exit 1
    fi

    # システム依存関係のチェック
    if ! check_system_dependencies; then
        exit 1
    fi

    # オプション解析
    case "${1:-}" in
        --setup)
            setup_venv
            print_info "セットアップが完了しました"
            print_info "アプリケーションを実行するには: $0"
            ;;
        --test)
            # venvがなければセットアップ
            if [ ! -d "$VENV_DIR" ]; then
                setup_venv
            fi
            run_tests
            ;;
        --help|-h)
            echo "使用方法:"
            echo "  $0           アプリケーションを実行"
            echo "  $0 --setup   環境セットアップのみ"
            echo "  $0 --test    テストを実行"
            echo "  $0 --help    このヘルプを表示"
            ;;
        "")
            # venvがなければセットアップ
            if [ ! -d "$VENV_DIR" ]; then
                setup_venv
                echo ""
            fi
            run_app
            ;;
        *)
            print_error "不明なオプション: $1"
            echo "ヘルプを表示するには: $0 --help"
            exit 1
            ;;
    esac
}

main "$@"
