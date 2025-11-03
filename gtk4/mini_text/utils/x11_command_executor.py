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
            # xclipでクリップボードにコピーする場合の特殊処理
            # xclipはクリップボード所有権を保持するためプロセスが終了しない
            # Popenでバックグラウンド起動し、標準入力を渡した後すぐに親プロセスに戻る
            if (
                len(command) >= 1
                and command[0] == "xclip"
                and input_data is not None
                and "-o" not in command  # 出力モードでない場合
            ):
                try:
                    # バックグラウンドでxclipを起動
                    # stdin=PIPEで標準入力を渡し、start_new_session=Trueで別セッションとして起動
                    process = subprocess.Popen(
                        command,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        start_new_session=True,
                    )

                    # communicate()でデータを渡し、短時間待機
                    try:
                        _, stderr = process.communicate(
                            input=input_data.encode("utf-8"), timeout=0.5
                        )
                        # プロセスが即座に終了した場合はエラー
                        if process.returncode is not None and process.returncode != 0:
                            return False, "", stderr.decode("utf-8", errors="replace")
                    except subprocess.TimeoutExpired:
                        # タイムアウト = プロセスがバックグラウンドで実行中 = 正常
                        # プロセスをそのまま残してクリップボード所有権を保持
                        pass

                    return True, "", ""

                except Exception as e:
                    return False, "", f"xclip実行エラー: {str(e)}"

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
