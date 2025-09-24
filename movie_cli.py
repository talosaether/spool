"""
Command-line interface adapter for the movie catalog application.

This module provides the CLI primary adapter for our hexagonal architecture.
It drives the application from the outside, translating user commands into
application service calls while providing a convenient command-line interface
for managing the movie catalog.

CLI adapter responsibilities:
- Parse command-line arguments and subcommands
- Coordinate application services (command and query)
- Format output for human consumption
- Provide test harness with pause functionality
- Handle errors gracefully with user-friendly messages
"""

import sys
import argparse
from typing import List, Optional, Dict, Any
from movie_domain import Movie, InvalidRatingError, InvalidTitleError, InvalidYearError
from movie_repository import MovieRepository, InvalidFilterError
from movie_command_service import MovieCommandService
from movie_query_service import MovieQueryService
from in_memory_repository import InMemoryMovieRepository


class MovieCLI:
    """
    Command-line interface adapter for movie catalog operations.

    This primary adapter translates command-line interactions into application
    service calls, providing a user-friendly interface for movie catalog
    management while demonstrating hexagonal architecture principles.

    CLI.Adapter.Primary -> external interface driving application services
    """

    def __init__(self, repository: MovieRepository):
        """
        Initialize CLI with repository and application services.

        Args:
            repository: MovieRepository implementation for data persistence

        CLI.Construction -> setup adapter with injected dependencies
        """
        # cli.dependency.repository -> injected storage abstraction
        self._repository: MovieRepository = repository

        # cli.services.application_layer -> create coordinated application services
        self._command_service: MovieCommandService = MovieCommandService(repository)
        self._query_service: MovieQueryService = MovieQueryService(repository)

    def run(self, args: Optional[List[str]] = None) -> None:
        """
        Execute CLI with provided arguments or sys.argv.

        Args:
            args: Optional list of command-line arguments (defaults to sys.argv[1:])

        CLI.Execution.Main -> primary entry point for command processing
        """
        # cli.argument.parsing -> setup argument parser with subcommands
        parser = self._create_argument_parser()

        # cli.argument.resolution -> parse provided or system arguments
        if args is None:
            args = sys.argv[1:]

        # cli.execution.parse_and_dispatch -> parse arguments and execute command
        try:
            parsed_args = parser.parse_args(args)
            # cli.dispatch.command -> route to appropriate command handler
            parsed_args.func(parsed_args)
        except AttributeError:
            # cli.error.no_command -> handle case where no subcommand provided
            parser.print_help()
        except (InvalidRatingError, InvalidTitleError, InvalidYearError, InvalidFilterError) as e:
            # cli.error.domain_validation -> handle domain validation errors
            self._print_error(f"Validation error: {e}")
            sys.exit(1)
        except Exception as e:
            # cli.error.unexpected -> handle unexpected system errors
            self._print_error(f"Unexpected error: {e}")
            sys.exit(1)

    def _create_argument_parser(self) -> argparse.ArgumentParser:
        """
        Create and configure the argument parser with all subcommands.

        Returns:
            Configured ArgumentParser with movie catalog subcommands

        CLI.Configuration.Parser -> setup command-line interface structure
        """
        # cli.parser.main -> primary argument parser configuration
        parser = argparse.ArgumentParser(
            description="Movie Catalog - Personal movie collection manager",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        # cli.parser.subcommands -> create subcommand system
        subparsers = parser.add_subparsers(
            title="Commands",
            description="Available movie catalog operations",
            help="Use 'command --help' for detailed help on each command"
        )

        # cli.subcommand.add -> movie addition command
        self._add_add_command(subparsers)

        # cli.subcommand.list -> movie listing command
        self._add_list_command(subparsers)

        # cli.subcommand.search -> movie search command
        self._add_search_command(subparsers)

        # cli.subcommand.rate -> movie rating command
        self._add_rate_command(subparsers)

        # cli.subcommand.tag -> movie tagging commands
        self._add_tag_commands(subparsers)

        # cli.subcommand.delete -> movie deletion command
        self._add_delete_command(subparsers)

        # cli.subcommand.stats -> catalog statistics command
        self._add_stats_command(subparsers)

        # cli.subcommand.test -> test harness command
        self._add_test_command(subparsers)

        return parser

    def _add_add_command(self, subparsers) -> None:
        """Add movie addition subcommand configuration."""
        add_parser = subparsers.add_parser("add", help="Add a new movie to the catalog")
        add_parser.add_argument("title", help="Movie title")
        add_parser.add_argument("year", type=int, help="Release year")
        add_parser.add_argument("description", help="Movie description or synopsis")
        add_parser.add_argument("--rating", type=float, help="Movie rating (1.0-10.0)")
        add_parser.add_argument("--tags", nargs="*", help="Movie tags/categories")
        add_parser.set_defaults(func=self._handle_add_command)

    def _add_list_command(self, subparsers) -> None:
        """Add movie listing subcommand configuration."""
        list_parser = subparsers.add_parser("list", help="List movies in the catalog")
        list_parser.add_argument("--year", type=int, help="Filter by release year")
        list_parser.add_argument("--min-rating", type=float, help="Minimum rating filter")
        list_parser.add_argument("--max-rating", type=float, help="Maximum rating filter")
        list_parser.add_argument("--tags", nargs="*", help="Filter by tags (must have all)")
        list_parser.set_defaults(func=self._handle_list_command)

    def _add_search_command(self, subparsers) -> None:
        """Add movie search subcommand configuration."""
        search_parser = subparsers.add_parser("search", help="Search movies by title")
        search_parser.add_argument("title", help="Title search term")
        search_parser.set_defaults(func=self._handle_search_command)

    def _add_rate_command(self, subparsers) -> None:
        """Add movie rating subcommand configuration."""
        rate_parser = subparsers.add_parser("rate", help="Rate a movie")
        rate_parser.add_argument("movie_id", help="Movie ID to rate")
        rate_parser.add_argument("rating", type=float, help="Rating (1.0-10.0)")
        rate_parser.set_defaults(func=self._handle_rate_command)

    def _add_tag_commands(self, subparsers) -> None:
        """Add movie tagging subcommand configurations."""
        tag_parser = subparsers.add_parser("tag", help="Add tag to a movie")
        tag_parser.add_argument("movie_id", help="Movie ID to tag")
        tag_parser.add_argument("tag", help="Tag to add")
        tag_parser.set_defaults(func=self._handle_add_tag_command)

        untag_parser = subparsers.add_parser("untag", help="Remove tag from a movie")
        untag_parser.add_argument("movie_id", help="Movie ID to untag")
        untag_parser.add_argument("tag", help="Tag to remove")
        untag_parser.set_defaults(func=self._handle_remove_tag_command)

    def _add_delete_command(self, subparsers) -> None:
        """Add movie deletion subcommand configuration."""
        delete_parser = subparsers.add_parser("delete", help="Delete a movie from catalog")
        delete_parser.add_argument("movie_id", help="Movie ID to delete")
        delete_parser.set_defaults(func=self._handle_delete_command)

    def _add_stats_command(self, subparsers) -> None:
        """Add catalog statistics subcommand configuration."""
        stats_parser = subparsers.add_parser("stats", help="Show catalog statistics")
        stats_parser.set_defaults(func=self._handle_stats_command)

    def _add_test_command(self, subparsers) -> None:
        """Add test harness subcommand configuration."""
        test_parser = subparsers.add_parser("test", help="Run tests with interactive pause")
        test_parser.set_defaults(func=self._handle_test_command)

    def _handle_add_command(self, args) -> None:
        """Handle movie addition command."""
        movie = self._command_service.add_movie(
            title=args.title,
            year=args.year,
            description=args.description,
            rating=args.rating,
            tags=args.tags
        )
        print(f"✓ Added movie: {movie.title} ({movie.year})")
        print(f"  ID: {movie.id}")
        if movie.rating:
            print(f"  Rating: {movie.rating}/10")
        if movie.tags:
            print(f"  Tags: {', '.join(movie.tags)}")

    def _handle_list_command(self, args) -> None:
        """Handle movie listing command."""
        movies = self._query_service.search_movies(
            year=args.year,
            rating_min=args.min_rating,
            rating_max=args.max_rating,
            tags=args.tags
        )

        if not movies:
            print("No movies found matching the criteria.")
            return

        print(f"Found {len(movies)} movie(s):")
        for movie in movies:
            self._print_movie_summary(movie)

    def _handle_search_command(self, args) -> None:
        """Handle movie search command."""
        movies = self._query_service.search_movies_by_title(args.title)

        if not movies:
            print(f"No movies found matching title: {args.title}")
            return

        print(f"Found {len(movies)} movie(s) matching '{args.title}':")
        for movie in movies:
            self._print_movie_summary(movie)

    def _handle_rate_command(self, args) -> None:
        """Handle movie rating command."""
        success = self._command_service.rate_movie(args.movie_id, args.rating)

        if success:
            movie = self._query_service.get_movie_by_id(args.movie_id)
            print(f"✓ Rated '{movie.title}': {args.rating}/10")
        else:
            print(f"✗ Movie with ID '{args.movie_id}' not found")

    def _handle_add_tag_command(self, args) -> None:
        """Handle add tag command."""
        success = self._command_service.add_tag_to_movie(args.movie_id, args.tag)

        if success:
            movie = self._query_service.get_movie_by_id(args.movie_id)
            print(f"✓ Added tag '{args.tag}' to '{movie.title}'")
        else:
            print(f"✗ Movie with ID '{args.movie_id}' not found")

    def _handle_remove_tag_command(self, args) -> None:
        """Handle remove tag command."""
        success = self._command_service.remove_tag_from_movie(args.movie_id, args.tag)

        if success:
            movie = self._query_service.get_movie_by_id(args.movie_id)
            print(f"✓ Removed tag '{args.tag}' from '{movie.title}'")
        else:
            print(f"✗ Movie with ID '{args.movie_id}' not found")

    def _handle_delete_command(self, args) -> None:
        """Handle movie deletion command."""
        # cli.operation.pre_delete_info -> get movie info before deletion for confirmation
        movie = self._query_service.get_movie_by_id(args.movie_id)

        if not movie:
            print(f"✗ Movie with ID '{args.movie_id}' not found")
            return

        success = self._command_service.delete_movie(args.movie_id)

        if success:
            print(f"✓ Deleted movie: {movie.title} ({movie.year})")
        else:
            print(f"✗ Failed to delete movie with ID '{args.movie_id}'")

    def _handle_stats_command(self, args) -> None:
        """Handle catalog statistics command."""
        stats = self._query_service.get_catalog_statistics()

        print("=== Movie Catalog Statistics ===")
        print(f"Total movies: {stats['total_movies']}")
        print(f"Movies with ratings: {stats['movies_with_ratings']}")

        if stats['movies_with_ratings'] > 0:
            print(f"Average rating: {stats['average_rating']}/10")

        if stats['year_range']:
            min_year, max_year = stats['year_range']
            print(f"Year range: {min_year} - {max_year}")

        if stats['unique_tags']:
            print(f"Unique tags ({len(stats['unique_tags'])}): {', '.join(sorted(stats['unique_tags']))}")

    def _handle_test_command(self, args) -> None:
        """
        Handle test command with interactive pause functionality.

        CLI.Test_Harness -> run tests with sample data and pause for exploration
        """
        print("🧪 Running movie catalog tests...")

        # cli.test.sample_data -> create sample movies for testing
        self._create_sample_test_data()

        print("✅ All tests completed successfully!")
        print()

        # cli.test.pause_interactive -> flush output and pause for user interaction
        sys.stdout.flush()

        print("🔧 Test environment active with sample data")
        print("CLI commands available:")
        print("  python -m movie_catalog list                    # List all movies")
        print("  python -m movie_catalog search <title>          # Search movies")
        print("  python -m movie_catalog add <title> <year> <desc> # Add movie")
        print("  python -m movie_catalog stats                   # Show statistics")
        print()
        print("Destroy test environment: Ctrl+C or type 'exit'")
        print()

        # cli.test.interactive_loop -> wait for user commands or exit
        try:
            while True:
                user_input = input("test> ").strip()
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                elif user_input:
                    # cli.test.command_execution -> execute user command in test context
                    try:
                        self.run(user_input.split())
                    except SystemExit:
                        # cli.test.error_recovery -> continue after command errors
                        continue
                print()
        except KeyboardInterrupt:
            pass

        print("\n🗑️  Test environment destroyed")

    def _create_sample_test_data(self) -> None:
        """Create sample data for test environment."""
        sample_movies = [
            ("The Matrix", 1999, "A computer programmer discovers reality is a simulation", 9.0, ["sci-fi", "action"]),
            ("Inception", 2010, "Dreams within dreams heist movie", 8.8, ["sci-fi", "thriller"]),
            ("The Godfather", 1972, "The aging patriarch transfers control to his son", 9.2, ["drama", "crime"]),
            ("Pulp Fiction", 1994, "Interconnected criminal stories in Los Angeles", 8.9, ["crime", "drama"]),
            ("Unrated Movie", 2023, "A movie without a rating yet", None, ["mystery"])
        ]

        for title, year, desc, rating, tags in sample_movies:
            self._command_service.add_movie(title, year, desc, rating, tags)

    def _print_movie_summary(self, movie: Movie) -> None:
        """Print formatted movie summary."""
        rating_str = f"{movie.rating}/10" if movie.rating else "Unrated"
        tags_str = f" [{', '.join(movie.tags)}]" if movie.tags else ""

        print(f"  • {movie.title} ({movie.year}) - {rating_str}{tags_str}")
        print(f"    ID: {movie.id}")
        print(f"    {movie.description}")

    def _print_error(self, message: str) -> None:
        """Print error message to stderr."""
        print(f"Error: {message}", file=sys.stderr)


def main() -> None:
    """
    Main entry point for the movie catalog CLI.

    CLI.Main -> primary application entry point
    """
    # cli.main.repository -> create in-memory repository for CLI usage
    repository = InMemoryMovieRepository()

    # cli.main.adapter -> create and run CLI adapter
    cli = MovieCLI(repository)
    cli.run()


if __name__ == "__main__":
    main()