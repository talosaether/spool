"""
Demo script to test the CLI functionality programmatically.

This demonstrates the CLI adapter working with the hexagonal architecture.
"""

from movie_cli import MovieCLI
from in_memory_repository import InMemoryMovieRepository


def demo_cli_operations():
    """Demonstrate CLI operations programmatically."""
    print("=== Movie Catalog CLI Demo ===\n")

    # Create shared repository and CLI instance
    repository = InMemoryMovieRepository()
    cli = MovieCLI(repository)

    print("1. Adding movies...")
    cli.run(["add", "The Matrix", "1999", "A computer programmer discovers reality is a simulation", "--rating", "9.0", "--tags", "sci-fi", "action"])
    cli.run(["add", "Inception", "2010", "Dreams within dreams", "--rating", "8.8", "--tags", "sci-fi", "thriller"])
    cli.run(["add", "The Godfather", "1972", "Mafia family drama", "--rating", "9.2", "--tags", "drama", "crime"])

    print("\n2. Listing all movies...")
    cli.run(["list"])

    print("\n3. Searching for sci-fi movies...")
    cli.run(["list", "--tags", "sci-fi"])

    print("\n4. Searching by title...")
    cli.run(["search", "Matrix"])

    print("\n5. Showing catalog statistics...")
    cli.run(["stats"])

    print("\n=== CLI Demo Complete ===")


if __name__ == "__main__":
    demo_cli_operations()