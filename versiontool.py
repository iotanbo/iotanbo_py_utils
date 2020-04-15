"""
Bump version, rebuild distribution or publish on pypi.org
"""
import shutil
import subprocess
import sys
import os


def _print_usage_hint():
    print(f"versiontool is a utility for bumping version, \n"
          f"recreating dist and publishing on pypi.org\n"
          f"Make sure that all tests pass before you proceed.")
    print(f"Usage:")
    print(f"    * bump version: 'python3 versiontool.py bump (major, minor, patch)'")
    print(f"    * rebuild dist: 'python3 versiontool.py rebuild'")
    print(f"    * publish on pypi.org: 'python3 versiontool.py publish'")


def _remove_dir(path: str) -> None:
    try:
        shutil.rmtree(path)
    except Exception:
        pass


def main():
    args = sys.argv
    if len(args) < 2:
        _print_usage_hint()
        exit(0)
    cmd = args[1]
    if cmd == "bump":
        if len(args) < 3:
            _print_usage_hint()
            exit(0)
        cmd = args[2]
        if cmd == "major" or cmd == "minor" or cmd == "patch":
            print(f"Bumping {cmd}...")
            subprocess.check_call(("bumpversion", "--allow-dirty", cmd), env=dict(os.environ))
            print("Done")
            exit(0)
        _print_usage_hint()
        exit(0)
    elif cmd == "rebuild":
        print("Rebuilding distribution...")
        _remove_dir("./dist")
        _remove_dir("./build")
        print(f"Creating new distribution...")
        subprocess.check_call(("python3", "setup.py", "sdist", "bdist_wheel"), env=dict(os.environ))
        print("Done")
        exit(0)
    elif cmd == "publish":
        print("Publishing on pypi.org...")
        subprocess.check_call(("twine", "upload", "dist/*"), env=dict(os.environ))
        print("Done")
        exit(0)
    else:
        print(args)
        _print_usage_hint()
        exit(0)


if __name__ == '__main__':
    main()
