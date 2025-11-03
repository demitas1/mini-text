"""X11CommandExecutorのpytestテスト"""

import pytest
from mini_text.utils.x11_command_executor import X11CommandExecutor


def test_execute_simple_command():
    """単純なコマンド実行が成功することを確認"""
    success, stdout, stderr = X11CommandExecutor.execute(["echo", "test"])

    assert success, "echoコマンドは成功すべき"
    assert "test" in stdout, "stdoutにtestが含まれるべき"
    assert stderr == "", "stderrは空であるべき"


def test_execute_with_input_data():
    """標準入力を使用したコマンド実行が成功することを確認"""
    # catコマンドで標準入力をそのまま出力
    success, stdout, stderr = X11CommandExecutor.execute(["cat"], input_data="テスト入力")

    assert success, "catコマンドは成功すべき"
    assert "テスト入力" in stdout, "stdoutに入力データが含まれるべき"


def test_execute_nonexistent_command():
    """存在しないコマンドの実行が適切に失敗することを確認"""
    success, stdout, stderr = X11CommandExecutor.execute(["nonexistent_command_12345"])

    assert not success, "存在しないコマンドは失敗すべき"
    assert "見つかりません" in stderr, "エラーメッセージに'見つかりません'が含まれるべき"


def test_execute_command_with_error():
    """エラーを返すコマンドが適切に処理されることを確認"""
    # ls で存在しないディレクトリを指定
    success, stdout, stderr = X11CommandExecutor.execute(
        ["ls", "/nonexistent_directory_12345"]
    )

    assert not success, "エラーコマンドは失敗すべき"
    assert stderr != "", "stderrにエラーメッセージが含まれるべき"


def test_return_types():
    """戻り値の型が正しいことを確認"""
    success, stdout, stderr = X11CommandExecutor.execute(["echo", "test"])

    assert isinstance(success, bool)
    assert isinstance(stdout, str)
    assert isinstance(stderr, str)
