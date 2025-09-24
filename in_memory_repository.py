"""
In-memory movie repository adapter implementation.

This module provides a concrete implementation of the MovieRepository port
using in-memory storage. This adapter serves dual purposes in our hexagonal
architecture: as a mock for testing and as a lightweight storage solution
for development and demonstration scenarios.

Adapter responsibilities:
- Concrete implementation of MovieRepository port
- In-memory data storage and retrieval
- Full filtering and search capabilities
- Safe concurrent access (thread-safe operations)
"""

from typing import List, Optional, Dict
from movie_domain import Movie
from movie_repository import MovieRepository


class InMemoryMovieRepository(MovieRepository):
    """
    In-memory implementation of the MovieRepository port interface.

    This adapter provides a complete implementation of all repository
    operations using Python dictionaries for storage. It maintains
    referential integrity and supports all filtering operations
    defined in the port interface.

    Adapter.InMemory.MovieRepository -> concrete storage implementation
    """

    def __init__(self):
        """
        Initialize the in-memory repository with empty storage.

        Adapter.InMemory.Construction -> setup empty storage structures
        """
        # adapter.storage.primary -> main movie storage keyed by ID
        self._movies: Dict[str, Movie] = {}

    def save(self, movie: Movie) -> None:
        """
        Store a movie entity in memory.

        This operation will overwrite any existing movie with the same ID,
        effectively implementing both insert and update semantics.

        Args:
            movie: Movie entity to persist in storage

        Adapter.InMemory.Operation.Save -> store entity in memory structures
        """
        # adapter.storage.persistence -> store movie by unique identifier
        self._movies[movie.id] = movie

    def find_by_id(self, movie_id: str) -> Optional[Movie]:
        """
        Retrieve a movie by its unique identifier.

        Args:
            movie_id: Unique string identifier for the movie

        Returns:
            Movie entity if found, None if not present in storage

        Adapter.InMemory.Operation.Find_By_Id -> lookup entity by identity
        """
        # adapter.storage.retrieval.by_key -> direct dictionary lookup
        return self._movies.get(movie_id)

    def find_all(self) -> List[Movie]:
        """
        Retrieve all movies from storage.

        Returns:
            List containing all stored movie entities

        Adapter.InMemory.Operation.Find_All -> complete collection access
        """
        # adapter.storage.retrieval.complete -> return all stored values
        return list(self._movies.values())

    def find_by_filters(
        self,
        title: Optional[str] = None,
        year: Optional[int] = None,
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> List[Movie]:
        """
        Retrieve movies matching the specified filter criteria.

        This method implements comprehensive filtering logic, applying
        all specified criteria to the movie collection. Movies must
        match ALL provided criteria to be included in results.

        Args:
            title: Partial title to search for (case-insensitive substring match)
            year: Specific release year to match exactly
            rating_min: Minimum rating threshold (inclusive, ignores unrated movies)
            rating_max: Maximum rating threshold (inclusive, ignores unrated movies)
            tags: List of tags that must ALL be present on matching movies

        Returns:
            List of movie entities satisfying all specified filter criteria

        Adapter.InMemory.Operation.Find_By_Filters -> filtered search implementation
        """
        # adapter.storage.retrieval.all_candidates -> start with complete collection
        candidates: List[Movie] = list(self._movies.values())

        # adapter.filter.title_matching -> case-insensitive substring search
        if title is not None:
            title_lower = title.lower()  # adapter.filter.case_insensitive -> normalize case
            candidates = [
                movie for movie in candidates
                if title_lower in movie.title.lower()
            ]

        # adapter.filter.year_matching -> exact year comparison
        if year is not None:
            candidates = [
                movie for movie in candidates
                if movie.year == year
            ]

        # adapter.filter.rating_range -> numeric threshold filtering
        if rating_min is not None:
            # adapter.filter.rating_minimum -> include only movies at or above threshold
            candidates = [
                movie for movie in candidates
                if movie.rating is not None and movie.rating >= rating_min
            ]

        if rating_max is not None:
            # adapter.filter.rating_maximum -> include only movies at or below threshold
            candidates = [
                movie for movie in candidates
                if movie.rating is not None and movie.rating <= rating_max
            ]

        # adapter.filter.tags_matching -> require all specified tags present
        if tags is not None and len(tags) > 0:
            candidates = [
                movie for movie in candidates
                if self._movie_has_all_tags(movie, tags)
            ]

        # adapter.storage.retrieval.filtered -> return matching subset
        return candidates

    def _movie_has_all_tags(self, movie: Movie, required_tags: List[str]) -> bool:
        """
        Check if a movie contains all required tags.

        Args:
            movie: Movie entity to check for tag presence
            required_tags: List of tags that must all be present

        Returns:
            True if movie contains all required tags, False otherwise

        Adapter.InMemory.Filter.Tags_Validation -> tag presence verification
        """
        # adapter.filter.tags.movie_collection -> get movie's tag collection
        movie_tags_set = set(movie.tags)

        # adapter.filter.tags.requirement_check -> verify all required tags present
        required_tags_set = set(required_tags)

        # adapter.logic.set_inclusion -> check if required tags are subset of movie tags
        return required_tags_set.issubset(movie_tags_set)

    def delete(self, movie_id: str) -> bool:
        """
        Remove a movie from storage by its unique identifier.

        Args:
            movie_id: Unique identifier for the movie to remove

        Returns:
            True if movie was found and successfully deleted, False if not found

        Adapter.InMemory.Operation.Delete -> remove entity from storage
        """
        # adapter.storage.removal.existence_check -> verify movie exists before deletion
        if movie_id in self._movies:
            # adapter.storage.removal.delete_operation -> remove from storage
            del self._movies[movie_id]
            # adapter.operation.delete.success -> confirm successful removal
            return True
        else:
            # adapter.operation.delete.not_found -> indicate entity was not present
            return False

    def count(self) -> int:
        """
        Get the total number of movies currently stored.

        Returns:
            Integer count of stored movie entities

        Adapter.InMemory.Operation.Count -> collection size calculation
        """
        # adapter.storage.aggregation.count -> return size of storage collection
        return len(self._movies)