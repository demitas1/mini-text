"""X11コマンド実行ユーティリティ"""

import subprocess
from typing import Optional


class X11CommandExecutor:
    """xdotool/xclipコマンドの実行を担当するクラス"""

    @staticmethod
    def execute(
        command: list[str], input_data: Optional[str] = None
    ) -> tuple[bool, str, str]:
        """
        コマンドを実行

        Args:
            command: 実行するコマンドと引数のリスト
            input_data: 標準入力に渡すデータ(オプション)

        Returns:
            tuple[bool, str, str]: (成功したか, stdout, stderr)
        """
        try:
            # input_dataがある場合はbytesに変換
            input_bytes = input_data.encode("utf-8") if input_data else None

            # コマンドを実行
            result = subprocess.run(
                command,
                input=input_bytes,
                capture_output=True,
                timeout=10,  # タイムアウトを10秒に設定
            )

            # 出力をデコード
            stdout = result.stdout.decode("utf-8", errors="replace")
            stderr = result.stderr.decode("utf-8", errors="replace")

            # 成功判定
            success = result.returncode == 0

            return success, stdout, stderr

        except subprocess.TimeoutExpired:
            return False, "", "コマンドがタイムアウトしました"
        except FileNotFoundError:
            return False, "", f"コマンドが見つかりません: {command[0]}"
        except Exception as e:
            return False, "", f"コマンド実行エラー: {str(e)}"
