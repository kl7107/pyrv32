#!/usr/bin/env python3
"""Entry point so that `python -m tests` runs the full suite."""

from . import run_all_tests


def main() -> None:
    """Run all discovered unit tests."""
    run_all_tests()


if __name__ == "__main__":
    main()
