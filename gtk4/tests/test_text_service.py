"""TextServiceのpytestテスト"""

import pytest
from unittest.mock import Mock
from mini_text.services.text_service import TextService


@pytest.fixture
def mock_executor():
    """モックExecutorのフィクスチャ"""
    return Mock()


@pytest.fixture
def mock_window_service():
    """モックWindowServiceのフィクスチャ"""
    return Mock()


@pytest.fixture
def mock_clipboard_service():
    """モックClipboardServiceのフィクスチャ"""
    return Mock()


@pytest.fixture
def service(mock_executor, mock_window_service, mock_clipboard_service):
    """TextServiceのフィクスチャ"""
    return TextService(
        window_service=mock_window_service,
        clipboard_service=mock_clipboard_service,
        executor=mock_executor,
    )


def test_send_text_success(service, mock_executor, mock_window_service, mock_clipboard_service):
    """テキスト送信が成功することを確認"""
    # 各サービスのモック戻り値を設定
    mock_clipboard_service.copy_to_clipboard.return_value = (True, "")
    mock_window_service.activate_window.return_value = (True, "")
    mock_executor.execute.return_value = (True, "", "")

    success, error_msg = service.send_text("12345", "テストテキスト", 0.1, 0.1)

    # 成功することを確認
    assert success
    assert error_msg == ""

    # 各サービスが正しく呼ばれたことを確認
    mock_clipboard_service.copy_to_clipboard.assert_called_once_with("テストテキスト")
    mock_window_service.activate_window.assert_called_once_with("12345", 0.1)
    mock_executor.execute.assert_called_once_with(["xdotool", "key", "ctrl+v"])


def test_send_text_clipboard_failure(service, mock_window_service, mock_clipboard_service):
    """クリップボードコピー失敗時の処理を確認"""
    # クリップボードコピーが失敗
    mock_clipboard_service.copy_to_clipboard.return_value = (False, "クリップボードエラー")

    success, error_msg = service.send_text("12345", "テストテキスト", 0.1, 0.1)

    # 失敗することを確認
    assert not success
    assert "クリップボードエラー" in error_msg

    # ウィンドウアクティベートは実行されないことを確認
    mock_window_service.activate_window.assert_not_called()


def test_send_text_activate_failure(service, mock_executor, mock_window_service, mock_clipboard_service):
    """ウィンドウアクティベート失敗時の処理を確認"""
    # クリップボードコピーは成功、アクティベートが失敗
    mock_clipboard_service.copy_to_clipboard.return_value = (True, "")
    mock_window_service.activate_window.return_value = (False, "ウィンドウエラー")

    success, error_msg = service.send_text("12345", "テストテキスト", 0.1, 0.1)

    # 失敗することを確認
    assert not success
    assert "ウィンドウエラー" in error_msg

    # ペースト操作は実行されないことを確認
    mock_executor.execute.assert_not_called()


def test_send_text_paste_failure(service, mock_executor, mock_window_service, mock_clipboard_service):
    """ペースト操作失敗時の処理を確認"""
    # クリップボードとアクティベートは成功、ペーストが失敗
    mock_clipboard_service.copy_to_clipboard.return_value = (True, "")
    mock_window_service.activate_window.return_value = (True, "")
    mock_executor.execute.return_value = (False, "", "ペーストエラー")

    success, error_msg = service.send_text("12345", "テストテキスト", 0.1, 0.1)

    # 失敗することを確認
    assert not success
    assert "ペースト操作に失敗" in error_msg


def test_receive_text_success(service, mock_executor, mock_clipboard_service):
    """テキスト受信が成功することを確認"""
    # 各操作のモック戻り値を設定
    mock_executor.execute.return_value = (True, "", "")
    mock_clipboard_service.get_from_clipboard.return_value = (True, "受信したテキスト", "")

    success, text, error_msg = service.receive_text(0.0)

    # 成功することを確認
    assert success
    assert text == "受信したテキスト"
    assert error_msg == ""

    # Ctrl+A と Ctrl+C が実行されたことを確認
    assert mock_executor.execute.call_count == 2
    mock_clipboard_service.get_from_clipboard.assert_called_once()


def test_receive_text_select_all_failure(service, mock_executor):
    """全選択操作失敗時の処理を確認"""
    # Ctrl+Aが失敗
    mock_executor.execute.return_value = (False, "", "全選択エラー")

    success, text, error_msg = service.receive_text(0.0)

    # 失敗することを確認
    assert not success
    assert text == ""
    assert "全選択操作に失敗" in error_msg


def test_receive_text_copy_failure(service, mock_executor):
    """コピー操作失敗時の処理を確認"""
    # Ctrl+Aは成功、Ctrl+Cが失敗
    mock_executor.execute.side_effect = [
        (True, "", ""),  # Ctrl+A成功
        (False, "", "コピーエラー"),  # Ctrl+C失敗
    ]

    success, text, error_msg = service.receive_text(0.0)

    # 失敗することを確認
    assert not success
    assert text == ""
    assert "コピー操作に失敗" in error_msg


def test_receive_text_clipboard_get_failure(service, mock_executor, mock_clipboard_service):
    """クリップボード取得失敗時の処理を確認"""
    # Ctrl+A, Ctrl+Cは成功、クリップボード取得が失敗
    mock_executor.execute.return_value = (True, "", "")
    mock_clipboard_service.get_from_clipboard.return_value = (False, "", "クリップボード取得エラー")

    success, text, error_msg = service.receive_text(0.0)

    # 失敗することを確認
    assert not success
    assert text == ""
    assert "クリップボード取得エラー" in error_msg
