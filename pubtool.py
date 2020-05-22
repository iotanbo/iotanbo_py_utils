"""
Publish tool: bump version, rebuild distribution and publish on pypi.org
"""
import os
import shutil
import subprocess
import sys


def _print_usage_hint():
    print(f"Usage:")
    print(f"  1) Make sure that all tests pass (run 'tox' command)")
    print(f"  2) Bump version or patch: 'python3 pubtool.py bump (minor, major, patch)")
    print(f"  3) Rebuild the distribution: 'python3 pubtool.py rebuild")
    print(f"  4) Publish on pypi.org: 'python3 pubtool.py publish")
    print(f"  5) Commit changes and create version tag: 'git tag v1.0.0")
    print(f"  5) Push to github.com: 'git push origin master v1.0.0")


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
            print("Ok")
            exit(0)
        _print_usage_hint()
        exit(0)
    elif cmd == "rebuild":
        print("Rebuilding distribution...")
        _remove_dir("./dist")
        _remove_dir("./build")
        print(f"Creating new distribution...")
        subprocess.check_call(("python3", "setup.py", "sdist", "bdist_wheel"), env=dict(os.environ))
        print("Ok")
        exit(0)
    elif cmd == "publish":
        print("Publishing on pypi.org...")
        subprocess.check_call(("twine", "upload", "dist/*"), env=dict(os.environ))
        print("Ok")
        exit(0)
    else:
        print(args)
        _print_usage_hint()
        exit(0)


if __name__ == '__main__':
    main()
