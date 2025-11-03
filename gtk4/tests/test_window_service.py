"""WindowServiceのpytestテスト"""

import pytest
from unittest.mock import Mock
from mini_text.services.window_service import WindowService


@pytest.fixture
def mock_executor():
    """モックExecutorのフィクスチャ"""
    return Mock()


@pytest.fixture
def service(mock_executor):
    """WindowServiceのフィクスチャ"""
    return WindowService(mock_executor)


def test_get_window_list_success(service, mock_executor):
    """ウィンドウ一覧取得が成功することを確認"""
    # モックの戻り値を設定
    # xdotool search の戻り値
    mock_executor.execute.side_effect = [
        (True, "12345\n67890\n", ""),  # search結果
        (True, "テストウィンドウ1", ""),  # getwindowname for 12345
        (True, "テストウィンドウ2", ""),  # getwindowname for 67890
    ]

    result = service.get_window_list()

    # 結果を検証
    assert len(result) == 2
    assert result[0] == ("12345", "テストウィンドウ1")
    assert result[1] == ("67890", "テストウィンドウ2")


def test_get_window_list_search_failure(service, mock_executor):
    """ウィンドウ検索が失敗した場合の処理を確認"""
    # search コマンドが失敗
    mock_executor.execute.return_value = (False, "", "エラー")

    result = service.get_window_list()

    # 空のリストが返されることを確認
    assert result == []


def test_get_window_list_empty(service, mock_executor):
    """ウィンドウが存在しない場合の処理を確認"""
    # searchは成功するが結果が空
    mock_executor.execute.return_value = (True, "", "")

    result = service.get_window_list()

    # 空のリストが返されることを確認
    assert result == []


def test_activate_window_success(service, mock_executor):
    """ウィンドウアクティベートが成功することを確認"""
    # windowactivateが成功
    mock_executor.execute.return_value = (True, "", "")

    success, error_msg = service.activate_window("12345", 0.0)

    # 成功することを確認
    assert success
    assert error_msg == ""

    # 正しいコマンドが実行されたことを確認
    mock_executor.execute.assert_called_once_with(
        ["xdotool", "windowactivate", "--sync", "12345"]
    )


def test_activate_window_failure(service, mock_executor):
    """ウィンドウアクティベートが失敗した場合の処理を確認"""
    # windowactivateが失敗
    mock_executor.execute.return_value = (False, "", "ウィンドウが見つかりません")

    success, error_msg = service.activate_window("99999", 0.0)

    # 失敗することを確認
    assert not success
    assert "アクティブ化に失敗" in error_msg
