"""Foundation entrypoint placeholder for the notifier process."""

from . import get_app_name


def main() -> None:
    print(get_app_name())


if __name__ == "__main__":
    main()
