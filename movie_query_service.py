"""
Movie query service for the application layer.

This module provides the query service that handles all read-only operations
for movies in our hexagonal architecture. It implements sophisticated search
and filtering capabilities while maintaining strict separation from command
operations, following CQRS principles.

Application layer responsibilities:
- Orchestrate complex query operations
- Provide high-level search and filtering interfaces
- Calculate aggregate statistics and analytics
- Handle application-specific query logic
"""

from typing import List, Optional, Dict, Any, Set
from movie_domain import Movie
from movie_repository import MovieRepository


class MovieQueryService:
    """
    Application service for movie query operations.

    This service handles all read-only operations for movies in our catalog
    system. It provides sophisticated search capabilities, filtering options,
    and statistical analysis while maintaining separation from state-modifying
    operations.

    Application.Service.Query -> read-only operations coordinator
    """

    def __init__(self, repository: MovieRepository):
        """
        Initialize query service with repository dependency.

        Args:
            repository: MovieRepository implementation for data access operations

        Application.Service.Construction -> dependency injection for storage abstraction
        """
        # application.service.dependency.repository -> injected storage abstraction
        self._repository: MovieRepository = repository

    def get_all_movies(self) -> List[Movie]:
        """
        Retrieve all movies from the catalog.

        Returns:
            List containing all movies in the catalog, or empty list if none exist

        Raises:
            Repository exceptions: If retrieval operation fails

        Application.Service.Query.Get_All -> retrieve complete movie collection
        """
        # application.operation.retrieval.complete -> delegate to repository
        return self._repository.find_all()

    def get_movie_by_id(self, movie_id: str) -> Optional[Movie]:
        """
        Retrieve a specific movie by its unique identifier.

        Args:
            movie_id: Unique string identifier for the movie

        Returns:
            Movie entity if found, None if not present in catalog

        Raises:
            Repository exceptions: If retrieval operation fails

        Application.Service.Query.Get_By_Id -> retrieve single movie by identity
        """
        # application.operation.retrieval.by_identity -> delegate to repository
        return self._repository.find_by_id(movie_id)

    def search_movies_by_title(self, title: str) -> List[Movie]:
        """
        Search for movies by title substring (case-insensitive).

        Args:
            title: Partial or complete title to search for

        Returns:
            List of movies whose titles contain the search term

        Raises:
            Repository exceptions: If search operation fails

        Application.Service.Query.Search_Title -> text-based movie search
        """
        # application.operation.search.title -> delegate title filtering to repository
        return self._repository.find_by_filters(title=title)

    def get_movies_by_year(self, year: int) -> List[Movie]:
        """
        Retrieve all movies from a specific release year.

        Args:
            year: Release year to filter by

        Returns:
            List of movies released in the specified year

        Raises:
            Repository exceptions: If retrieval operation fails

        Application.Service.Query.Filter_Year -> temporal filtering operation
        """
        # application.operation.filter.year -> delegate year filtering to repository
        return self._repository.find_by_filters(year=year)

    def get_movies_by_rating_range(
        self,
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None
    ) -> List[Movie]:
        """
        Retrieve movies within a specific rating range.

        Movies without ratings are excluded from results. Either boundary
        can be omitted to create open-ended ranges.

        Args:
            rating_min: Minimum rating threshold (inclusive), None for no lower bound
            rating_max: Maximum rating threshold (inclusive), None for no upper bound

        Returns:
            List of movies with ratings within the specified range

        Raises:
            InvalidFilterError: If rating bounds are invalid
            Repository exceptions: If retrieval operation fails

        Application.Service.Query.Filter_Rating -> numeric range filtering operation
        """
        # application.operation.filter.rating_range -> delegate rating filtering to repository
        return self._repository.find_by_filters(
            rating_min=rating_min,
            rating_max=rating_max
        )

    def get_movies_by_tags(self, tags: List[str]) -> List[Movie]:
        """
        Retrieve movies that contain all specified tags.

        Args:
            tags: List of tags that must all be present on matching movies

        Returns:
            List of movies containing all specified tags

        Raises:
            Repository exceptions: If retrieval operation fails

        Application.Service.Query.Filter_Tags -> category-based filtering operation
        """
        # application.operation.filter.tags -> delegate tag filtering to repository
        return self._repository.find_by_filters(tags=tags)

    def search_movies(
        self,
        title: Optional[str] = None,
        year: Optional[int] = None,
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> List[Movie]:
        """
        Perform comprehensive movie search with multiple filter criteria.

        Movies must match ALL provided criteria to be included in results.
        Any combination of filters can be used, including using none at all
        (which returns all movies).

        Args:
            title: Partial title to search for (case-insensitive)
            year: Specific release year to match
            rating_min: Minimum rating threshold (inclusive)
            rating_max: Maximum rating threshold (inclusive)
            tags: List of tags that must all be present

        Returns:
            List of movies matching all specified criteria

        Raises:
            InvalidFilterError: If filter criteria are invalid
            Repository exceptions: If search operation fails

        Application.Service.Query.Search_Complex -> multi-criteria filtering operation
        """
        # application.operation.search.complex -> delegate comprehensive filtering to repository
        return self._repository.find_by_filters(
            title=title,
            year=year,
            rating_min=rating_min,
            rating_max=rating_max,
            tags=tags
        )

    def get_movie_count(self) -> int:
        """
        Get the total number of movies in the catalog.

        Returns:
            Integer count of movies currently in the catalog

        Raises:
            Repository exceptions: If count operation fails

        Application.Service.Query.Count -> collection size operation
        """
        # application.operation.aggregation.count -> delegate count to repository
        return self._repository.count()

    def get_catalog_statistics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics about the movie catalog.

        This method provides aggregate information including counts,
        averages, and collections of unique values across the catalog.

        Returns:
            Dictionary containing statistical information:
            - total_movies: Total number of movies
            - movies_with_ratings: Count of movies that have ratings
            - average_rating: Average rating across all rated movies
            - unique_tags: Set of all unique tags used in the catalog
            - year_range: Tuple of (earliest_year, latest_year) or None if no movies

        Raises:
            Repository exceptions: If data retrieval fails

        Application.Service.Query.Statistics -> aggregate information operation
        """
        # application.operation.retrieval.all_data -> get complete dataset for analysis
        all_movies = self._repository.find_all()
        total_count = self._repository.count()

        # application.calculation.statistics.initialization -> setup calculation variables
        movies_with_ratings = 0
        total_rating = 0.0
        unique_tags: Set[str] = set()
        years = []

        # application.calculation.statistics.aggregation -> process each movie for statistics
        for movie in all_movies:
            # application.statistics.rating.accumulation -> collect rating data
            if movie.rating is not None:
                movies_with_ratings += 1
                total_rating += movie.rating

            # application.statistics.tags.collection -> collect unique tags
            unique_tags.update(movie.tags)

            # application.statistics.years.collection -> collect year data
            years.append(movie.year)

        # application.calculation.rating.average -> compute average rating
        average_rating = round(total_rating / movies_with_ratings, 2) if movies_with_ratings > 0 else 0.0

        # application.calculation.years.range -> determine year span
        year_range = (min(years), max(years)) if years else None

        # application.service.result.statistics -> return comprehensive statistics
        return {
            "total_movies": total_count,
            "movies_with_ratings": movies_with_ratings,
            "average_rating": average_rating,
            "unique_tags": unique_tags,
            "year_range": year_range
        }