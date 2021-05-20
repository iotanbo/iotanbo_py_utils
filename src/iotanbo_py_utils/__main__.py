"""Command-line interface."""
import click

import iotanbo_py_utils


@click.command()
@click.version_option()
def main() -> None:
    """Iotanbo Python Utilities."""
    print(f"iotanbo_py_utils v{iotanbo_py_utils.__version__}")


if __name__ == "__main__":
    main(prog_name="iotanbo_py_utils")  # pragma: no cover
