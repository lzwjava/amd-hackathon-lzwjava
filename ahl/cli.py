"""ahl - A very simple CLI tool."""

import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="ahl",
        description="A very simple CLI tool - says hello!",
    )
    parser.add_argument(
        "-n", "--name",
        default="World",
        help="Who to greet (default: World)",
    )
    args = parser.parse_args()

    print(f"Hello, {args.name}! 👋")


if __name__ == "__main__":
    main()
