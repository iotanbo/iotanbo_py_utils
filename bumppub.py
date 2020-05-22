"""
Bump version and publish on pypi.org tool
"""
import os
import shutil
import subprocess
# import sys
import iotanbo_py_utils


def _remove_dir(path: str) -> None:
    try:
        shutil.rmtree(path)
    except Exception as e:
        print(f"Error while deleting dir '{path}': {e.__class__.__name__}, {str(e)}")


def main():
    current_version_str = iotanbo_py_utils.__version__
    current_version_list = current_version_str.split('.')

    major = int(current_version_list[0])
    minor = int(current_version_list[1])
    patch = int(current_version_list[2])
    print(f"Current 'iotanbo_py_utils' version is {current_version_str}")
    prompt = "Choose what to increment (1 - major, 2 - minor, 3 - patch, 0 - skip version change, q - quit): "
    choice = -1
    try:
        choice = input(prompt)
        choice = int(choice)
    except Exception:
        print("Wrong input, operation canceled.")
        exit(0)

    confirm = ""
    cmd = ()
    skip = False
    if choice == 0:
        print("Version bumping skipped.")
        confirm = 'y'
        skip = True
    elif choice == 1:
        confirm = input("Do you confirm bumping major version (y/n)? ")
        cmd = ("bumpversion", "--allow-dirty", "major")
        major += 1
    elif choice == 2:
        confirm = input("Do you confirm bumping minor version (y/n)? ")
        cmd = ("bumpversion", "--allow-dirty", "minor")
        minor += 1
    elif choice == 3:
        confirm = input("Do you confirm bumping patch (y/n)? ")
        cmd = ("bumpversion", "--allow-dirty", "patch")
        patch += 1
    else:
        print("Wrong input, operation canceled.")
        exit(0)
    if confirm != 'y':
        print("Canceled.")
        exit(0)

    if not skip:
        subprocess.check_call(cmd, env=dict(os.environ))

    # Rebuild distribution
    print("Rebuilding distribution...", end="")
    _remove_dir("./dist")
    _remove_dir("./build")

    subprocess.check_call(("python3", "setup.py", "sdist", "bdist_wheel"), env=dict(os.environ))
    print("Done.")

    subprocess.check_call(("git", "add", "."), env=dict(os.environ))
    commit_msg = input("Commit message (leave empty to cancel): ")
    if commit_msg:
        subprocess.check_call(("git", "commit", "-m", commit_msg), env=dict(os.environ))
        # Create new version tag
        new_tag = f"v{major}.{minor}.{patch}"
        subprocess.check_call(("git", "tag", new_tag), env=dict(os.environ))
        print("Done.")
    else:
        print("Canceled.")
        exit(0)

    choice = input("Do you wish to publish updated package on pypi.org (y/n)? ")
    if choice != 'y':
        print("Canceled.")
        exit(0)

    print("Publishing ...")
    subprocess.check_call(("twine", "upload", "dist/*"), env=dict(os.environ))
    print("Ok")

    # return
    #
    # args = sys.argv
    # if len(args) < 2:
    #     _print_usage_hint()
    #     exit(0)
    # cmd = args[1]
    # if cmd == "bump":
    #     if len(args) < 3:
    #         _print_usage_hint()
    #         exit(0)
    #     cmd = args[2]
    #     if cmd == "major" or cmd == "minor" or cmd == "patch":
    #         print(f"Bumping {cmd}...")
    #         subprocess.check_call(("bumpversion", "--allow-dirty", cmd), env=dict(os.environ))
    #         print("Ok")
    #         exit(0)
    #     _print_usage_hint()
    #     exit(0)
    # elif cmd == "rebuild":
    #     print("Rebuilding distribution...")
    #     _remove_dir("./dist")
    #     _remove_dir("./build")
    #     print(f"Creating new distribution...")
    #     subprocess.check_call(("python3", "setup.py", "sdist", "bdist_wheel"), env=dict(os.environ))
    #     print("Ok")
    #     exit(0)
    # elif cmd == "publish":
    #     print("Publishing on pypi.org...")
    #     subprocess.check_call(("twine", "upload", "dist/*"), env=dict(os.environ))
    #     print("Ok")
    #     exit(0)
    # else:
    #     print(args)
    #     _print_usage_hint()
    #     exit(0)


# def _print_usage_hint():
#     print(f"Usage:")
#     print(f"  1) Make sure that all tests pass (run 'tox' command)")
#     print(f"  2) Bump version or patch: 'python3 pubtool.py bump (minor, major, patch)")
#     print(f"  3) Rebuild the distribution: 'python3 pubtool.py rebuild")
#     print(f"  4) Publish on pypi.org: 'python3 pubtool.py publish")
#     print(f"  5) Commit changes and create version tag: 'git tag v1.0.0")
#     print(f"  5) Push to github.com: 'git push origin master v1.0.0")
#
#
# def _remove_dir(path: str) -> None:
#     try:
#         shutil.rmtree(path)
#     except Exception:
#         pass
#
#
# def main():
#     args = sys.argv
#     if len(args) < 2:
#         _print_usage_hint()
#         exit(0)
#     cmd = args[1]
#     if cmd == "bump":
#         if len(args) < 3:
#             _print_usage_hint()
#             exit(0)
#         cmd = args[2]
#         if cmd == "major" or cmd == "minor" or cmd == "patch":
#             print(f"Bumping {cmd}...")
#             subprocess.check_call(("bumpversion", "--allow-dirty", cmd), env=dict(os.environ))
#             print("Ok")
#             exit(0)
#         _print_usage_hint()
#         exit(0)
#     elif cmd == "rebuild":
#         print("Rebuilding distribution...")
#         _remove_dir("./dist")
#         _remove_dir("./build")
#         print(f"Creating new distribution...")
#         subprocess.check_call(("python3", "setup.py", "sdist", "bdist_wheel"), env=dict(os.environ))
#         print("Ok")
#         exit(0)
#     elif cmd == "publish":
#         print("Publishing on pypi.org...")
#         subprocess.check_call(("twine", "upload", "dist/*"), env=dict(os.environ))
#         print("Ok")
#         exit(0)
#     else:
#         print(args)
#         _print_usage_hint()
#         exit(0)

if __name__ == '__main__':
    main()
