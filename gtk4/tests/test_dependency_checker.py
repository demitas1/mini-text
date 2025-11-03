"""DependencyCheckerのpytestテスト"""

import pytest
from mini_text.utils.dependency_checker import DependencyChecker


def test_check_dependencies():
    """依存関係チェックが動作することを確認"""
    all_available, missing = DependencyChecker.check_dependencies()

    # 戻り値の型を確認
    assert isinstance(all_available, bool)
    assert isinstance(missing, list)

    # missingリストの要素が文字列であることを確認
    for tool in missing:
        assert isinstance(tool, str)

    # all_availableとmissingの整合性を確認
    if all_available:
        assert len(missing) == 0, "all_availableがTrueの場合、missingは空であるべき"
    else:
        assert len(missing) > 0, "all_availableがFalseの場合、missingに要素があるべき"


def test_required_commands_defined():
    """必要なコマンドリストが定義されていることを確認"""
    assert hasattr(DependencyChecker, "REQUIRED_COMMANDS")
    assert isinstance(DependencyChecker.REQUIRED_COMMANDS, list)
    assert len(DependencyChecker.REQUIRED_COMMANDS) > 0
