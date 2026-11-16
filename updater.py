# python
import sys
import os
import time
import shutil
import subprocess


def main():
    if len(sys.argv) < 3:
        return

    current_exe = os.path.abspath(sys.argv[1])
    new_exe = os.path.abspath(sys.argv[2])

    if not os.path.isfile(new_exe):
        return

    app_dir = os.path.dirname(current_exe)
    backup_exe = current_exe + ".bak"
    temp_exe = current_exe + ".new"

    # Main application ko band hone ka samay do
    time.sleep(3)

    try:
        # Nayi EXE ko pehle temporary file mein copy karo
        shutil.copy2(new_exe, temp_exe)

        # Purani EXE ka backup rakho
        if os.path.exists(backup_exe):
            os.remove(backup_exe)

        if os.path.exists(current_exe):
            os.replace(current_exe, backup_exe)

        try:
            # Nayi EXE ko original naam par rakho
            os.replace(temp_exe, current_exe)

        except Exception:
            # Replacement fail ho to backup restore karo
            if os.path.exists(backup_exe):
                os.replace(backup_exe, current_exe)
            raise

        # Downloaded temporary update file hatao
        if os.path.exists(new_exe):
            os.remove(new_exe)

        # Updated application start karo
        subprocess.Popen(
            [current_exe],
            cwd=app_dir
        )

    except Exception:
        # Temporary files ko safely clean karne ki koshish
        try:
            if os.path.exists(temp_exe):
                os.remove(temp_exe)
        except OSError:
            pass


if __name__ == "__main__":
    main()
