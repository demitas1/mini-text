"""依存関係チェックユーティリティ"""

import shutil


class DependencyChecker:
    """xdotoolのインストール確認を行うクラス"""

    # 必要な外部コマンドのリスト
    REQUIRED_COMMANDS = ["xdotool"]

    @staticmethod
    def check_dependencies() -> tuple[bool, list[str]]:
        """
        必要な外部コマンドがインストールされているかチェック

        Returns:
            tuple[bool, list[str]]: (全て利用可能か, 不足しているツールのリスト)
        """
        missing_tools = []

        for command in DependencyChecker.REQUIRED_COMMANDS:
            # shutil.which()でコマンドの存在を確認
            if shutil.which(command) is None:
                missing_tools.append(command)

        # 全てのツールが利用可能ならTrue
        all_available = len(missing_tools) == 0

        return all_available, missing_tools
