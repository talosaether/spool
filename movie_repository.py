"""
Movie repository port interface and related value objects.

This module defines the abstract repository interface (port) in our hexagonal
architecture. It establishes the contract between the domain layer and storage
adapters, enabling dependency inversion and testability.

Port responsibilities:
- Abstract interface for movie storage operations
- Filter value objects for search criteria
- Storage operation contracts (save, find, delete, count)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from movie_domain import Movie


class InvalidFilterError(ValueError):
    """
    Raised when filter criteria violate business rules.

    Domain.Exception.Filter -> business rule violation for search criteria
    """
    pass


class MovieFilters:
    """
    Value object encapsulating movie search and filter criteria.

    This value object represents search criteria for finding movies
    in the catalog. It encapsulates validation logic and provides
    a clean interface for complex filtering operations.

    Domain.ValueObject.MovieFilters -> search criteria encapsulation
    """

    def __init__(
        self,
        title: Optional[str] = None,
        year: Optional[int] = None,
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Initialize movie filter criteria with validation.

        Args:
            title: Partial title to search for (domain.filter.text_search.title)
            year: Specific release year (domain.filter.exact_match.year)
            rating_min: Minimum rating threshold (domain.filter.range.rating_lower)
            rating_max: Maximum rating threshold (domain.filter.range.rating_upper)
            tags: List of required tags (domain.filter.collection.tags)

        Raises:
            InvalidFilterError: If filter criteria violate business rules

        Domain.ValueObject.Construction -> filter criteria with validation
        """
        # domain.filter.text.title -> optional partial text matching
        self._title: Optional[str] = title.strip() if title else None

        # domain.filter.temporal.year -> optional exact year matching
        self._year: Optional[int] = year

        # domain.filter.rating.bounds -> optional numeric range filtering
        self._rating_min: Optional[float] = None
        self._rating_max: Optional[float] = None

        # domain.filter.validation.rating_range -> validate rating criteria
        if rating_min is not None or rating_max is not None:
            self._validate_and_set_rating_range(rating_min, rating_max)

        # domain.filter.classification.tags -> optional category filtering
        self._tags: List[str] = tags.copy() if tags else []

    def _validate_and_set_rating_range(
        self,
        rating_min: Optional[float],
        rating_max: Optional[float]
    ) -> None:
        """
        Validate and set rating range filter criteria.

        Args:
            rating_min: Proposed minimum rating threshold
            rating_max: Proposed maximum rating threshold

        Raises:
            InvalidFilterError: If rating range is invalid

        Domain.Filter.Validation.Rating_Range -> business rule for rating bounds
        """
        # domain.validation.rating.absolute_bounds -> same as movie entity bounds
        min_valid_rating: float = 1.0
        max_valid_rating: float = 10.0

        # domain.validation.filter.rating_minimum -> minimum rating bound check
        if rating_min is not None:
            if rating_min < min_valid_rating or rating_min > max_valid_rating:
                raise InvalidFilterError(
                    f"Minimum rating {rating_min} must be between {min_valid_rating} and {max_valid_rating}"
                )
            self._rating_min = rating_min

        # domain.validation.filter.rating_maximum -> maximum rating bound check
        if rating_max is not None:
            if rating_max < min_valid_rating or rating_max > max_valid_rating:
                raise InvalidFilterError(
                    f"Maximum rating {rating_max} must be between {min_valid_rating} and {max_valid_rating}"
                )
            self._rating_max = rating_max

        # domain.validation.filter.rating_range_logic -> min cannot exceed max
        if (self._rating_min is not None and
            self._rating_max is not None and
            self._rating_min > self._rating_max):
            raise InvalidFilterError(
                f"Minimum rating {self._rating_min} cannot exceed maximum rating {self._rating_max}"
            )

    @property
    def title(self) -> Optional[str]:
        """
        Get the title search criterion.

        Returns:
            Title text to search for, or None if no title filter

        Domain.Filter.Access.Title -> text-based search criterion
        """
        return self._title

    @property
    def year(self) -> Optional[int]:
        """
        Get the year filter criterion.

        Returns:
            Specific year to match, or None if no year filter

        Domain.Filter.Access.Year -> temporal filtering criterion
        """
        return self._year

    @property
    def rating_min(self) -> Optional[float]:
        """
        Get the minimum rating filter criterion.

        Returns:
            Minimum rating threshold, or None if no minimum filter

        Domain.Filter.Access.Rating_Min -> lower bound rating criterion
        """
        return self._rating_min

    @property
    def rating_max(self) -> Optional[float]:
        """
        Get the maximum rating filter criterion.

        Returns:
            Maximum rating threshold, or None if no maximum filter

        Domain.Filter.Access.Rating_Max -> upper bound rating criterion
        """
        return self._rating_max

    @property
    def tags(self) -> List[str]:
        """
        Get the tags filter criteria.

        Returns:
            List of required tags (defensive copy)

        Domain.Filter.Access.Tags -> category filtering criteria
        """
        # domain.encapsulation.defensive_copy -> prevent external mutation
        return self._tags.copy()

    def is_empty(self) -> bool:
        """
        Check if this filter has no criteria set.

        Returns:
            True if no filtering criteria are specified

        Domain.Filter.State.Empty_Check -> detect no-filter condition
        """
        # domain.filter.state.empty_detection -> check all criteria unset
        return (
            self._title is None and
            self._year is None and
            self._rating_min is None and
            self._rating_max is None and
            len(self._tags) == 0
        )


class MovieRepository(ABC):
    """
    Abstract repository interface for movie storage operations.

    This port defines the contract between the domain layer and storage
    adapters in our hexagonal architecture. It enables dependency inversion
    by allowing the domain to depend on this abstraction rather than
    concrete storage implementations.

    Domain.Port.Repository -> storage abstraction interface
    """

    @abstractmethod
    def save(self, movie: Movie) -> None:
        """
        Persist a movie entity to storage.

        Args:
            movie: Movie entity to store

        Domain.Port.Repository.Save -> persistence operation contract
        """
        # domain.operation.persistence.save -> abstract storage operation
        pass

    @abstractmethod
    def find_by_id(self, movie_id: str) -> Optional[Movie]:
        """
        Retrieve a movie by its unique identifier.

        Args:
            movie_id: Unique identifier for the movie

        Returns:
            Movie entity if found, None otherwise

        Domain.Port.Repository.Find_By_Id -> retrieval by identity contract
        """
        # domain.operation.retrieval.by_id -> abstract identity lookup
        pass

    @abstractmethod
    def find_all(self) -> List[Movie]:
        """
        Retrieve all movies from storage.

        Returns:
            List of all stored movie entities

        Domain.Port.Repository.Find_All -> complete collection retrieval contract
        """
        # domain.operation.retrieval.all -> abstract collection access
        pass

    @abstractmethod
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

        Args:
            title: Partial title to search for (case-insensitive)
            year: Specific release year to match
            rating_min: Minimum rating threshold (inclusive)
            rating_max: Maximum rating threshold (inclusive)
            tags: List of tags that must all be present on matching movies

        Returns:
            List of movie entities matching all specified criteria

        Domain.Port.Repository.Find_By_Filters -> filtered search contract
        """
        # domain.operation.retrieval.filtered -> abstract search operation
        pass

    @abstractmethod
    def delete(self, movie_id: str) -> bool:
        """
        Remove a movie from storage by its unique identifier.

        Args:
            movie_id: Unique identifier for the movie to remove

        Returns:
            True if movie was found and deleted, False if not found

        Domain.Port.Repository.Delete -> removal operation contract
        """
        # domain.operation.removal.by_id -> abstract deletion operation
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Get the total number of movies in storage.

        Returns:
            Integer count of stored movie entities

        Domain.Port.Repository.Count -> collection size contract
        """
        # domain.operation.aggregation.count -> abstract size operation
        pass