"""
Entry point for running the movie catalog as a Python module.

This allows the movie catalog to be executed using:
python -m movie_catalog [commands...]
"""

from movie_cli import main

if __name__ == "__main__":
    main()