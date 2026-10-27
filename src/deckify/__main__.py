"""Allow `python -m deckify`."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
