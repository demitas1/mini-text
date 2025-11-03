"""ClipboardServiceのpytestテスト"""

import pytest
from unittest.mock import Mock
from mini_text.services.clipboard_service import ClipboardService


@pytest.fixture
def mock_executor():
    """モックExecutorのフィクスチャ"""
    return Mock()


@pytest.fixture
def service(mock_executor):
    """ClipboardServiceのフィクスチャ"""
    return ClipboardService(mock_executor)


def test_copy_to_clipboard_success(service, mock_executor):
    """クリップボードへのコピーが成功することを確認"""
    # xclipコマンドが成功
    mock_executor.execute.return_value = (True, "", "")

    success, error_msg = service.copy_to_clipboard("テストテキスト")

    # 成功することを確認
    assert success
    assert error_msg == ""

    # 正しいコマンドが実行されたことを確認
    mock_executor.execute.assert_called_once_with(
        ["xclip", "-i", "-selection", "clipboard"], input_data="テストテキスト"
    )


def test_copy_to_clipboard_failure(service, mock_executor):
    """クリップボードへのコピーが失敗した場合の処理を確認"""
    # xclipコマンドが失敗
    mock_executor.execute.return_value = (False, "", "xclipエラー")

    success, error_msg = service.copy_to_clipboard("テストテキスト")

    # 失敗することを確認
    assert not success
    assert "コピーに失敗" in error_msg


def test_get_from_clipboard_success(service, mock_executor):
    """クリップボードからの取得が成功することを確認"""
    # xclipコマンドが成功
    mock_executor.execute.return_value = (True, "取得したテキスト", "")

    success, text, error_msg = service.get_from_clipboard()

    # 成功することを確認
    assert success
    assert text == "取得したテキスト"
    assert error_msg == ""

    # 正しいコマンドが実行されたことを確認
    mock_executor.execute.assert_called_once_with(
        ["xclip", "-selection", "clipboard", "-o"]
    )


def test_get_from_clipboard_failure(service, mock_executor):
    """クリップボードからの取得が失敗した場合の処理を確認"""
    # xclipコマンドが失敗
    mock_executor.execute.return_value = (False, "", "xclipエラー")

    success, text, error_msg = service.get_from_clipboard()

    # 失敗することを確認
    assert not success
    assert text == ""
    assert "取得に失敗" in error_msg


def test_copy_empty_string(service, mock_executor):
    """空文字列のコピーが正常に処理されることを確認"""
    # xclipコマンドが成功
    mock_executor.execute.return_value = (True, "", "")

    success, error_msg = service.copy_to_clipboard("")

    # 成功することを確認
    assert success

    # 空文字列でコマンドが実行されたことを確認
    mock_executor.execute.assert_called_once_with(
        ["xclip", "-i", "-selection", "clipboard"], input_data=""
    )
