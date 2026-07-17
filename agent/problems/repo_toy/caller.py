"""Caller module in the toy repo."""

from app import greet


def main() -> None:
    print(greet("agent"))


if __name__ == "__main__":
    main()
