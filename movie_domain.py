"""
Movie catalog domain entities and business logic.

This module contains the core domain layer of our hexagonal architecture.
It defines entities, value objects, and domain services that encapsulate
the business rules for managing a personal movie catalog.

Domain responsibilities:
- Movie entity with validation
- Business rules for ratings, years, titles
- Identity management for movies
"""

import uuid
from datetime import datetime
from typing import List, Optional


class InvalidRatingError(ValueError):
    """
    Raised when movie rating is outside valid range.

    Domain.Exception.Rating -> business rule violation for rating bounds
    """
    pass


class InvalidYearError(ValueError):
    """
    Raised when movie year is unrealistic.

    Domain.Exception.Year -> business rule violation for production year
    """
    pass


class InvalidTitleError(ValueError):
    """
    Raised when movie title is empty or invalid.

    Domain.Exception.Title -> business rule violation for title content
    """
    pass


class Movie:
    """
    Core domain entity representing a cataloged movie.

    This entity encapsulates all business rules for what constitutes
    a valid movie in our catalog system. It maintains identity,
    enforces validation constraints, and provides behavior for
    updating movie attributes.

    Domain.Entity.Movie -> central aggregate root for movie catalog
    """

    def __init__(
        self,
        title: str,
        year: int,
        description: str,
        rating: Optional[float] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Initialize a new Movie entity with validation.

        Args:
            title: Human-readable movie title (domain.movie.identity.title)
            year: Release year for the movie (domain.movie.metadata.year)
            description: Plot synopsis or description (domain.movie.content.description)
            rating: Optional numeric rating 1.0-10.0 (domain.movie.evaluation.rating)
            tags: Optional list of categorization strings (domain.movie.classification.tags)

        Raises:
            InvalidTitleError: If title is empty or whitespace-only
            InvalidYearError: If year is outside reasonable bounds
            InvalidRatingError: If rating is outside 1.0-10.0 range

        Domain.Movie.Construction -> entity creation with business rule enforcement
        """
        # domain.movie.identity.unique_id -> auto-generated UUID for entity identity
        self._id: str = str(uuid.uuid4())

        # domain.movie.validation.title -> ensure meaningful title content
        self._validate_and_set_title(title)

        # domain.movie.validation.year -> ensure realistic production year
        self._validate_and_set_year(year)

        # domain.movie.content.description -> descriptive text content
        self._description: str = description

        # domain.movie.evaluation.rating -> optional numeric assessment
        self._rating: Optional[float] = None
        if rating is not None:
            self._validate_and_set_rating(rating)

        # domain.movie.classification.tags -> collection of category strings
        self._tags: List[str] = tags.copy() if tags else []

    def _validate_and_set_title(self, title: str) -> None:
        """
        Validate and set the movie title.

        Args:
            title: Proposed title string

        Raises:
            InvalidTitleError: If title is empty or whitespace-only

        Domain.Movie.Validation.Title -> business rule for meaningful titles
        """
        # domain.validation.title.content_check -> ensure non-empty meaningful content
        if not title or not title.strip():
            raise InvalidTitleError("Movie title cannot be empty or whitespace-only")

        # domain.movie.attribute.title -> store validated title
        self._title: str = title.strip()

    def _validate_and_set_year(self, year: int) -> None:
        """
        Validate and set the movie production year.

        Args:
            year: Proposed production year

        Raises:
            InvalidYearError: If year is outside reasonable bounds

        Domain.Movie.Validation.Year -> business rule for realistic production years
        """
        # domain.time.reference.current -> current calendar year for validation
        current_year: int = datetime.now().year

        # domain.validation.year.historical_minimum -> first motion pictures circa 1888
        min_year: int = 1888

        # domain.validation.year.future_maximum -> reasonable future production buffer
        max_year: int = current_year + 10

        # domain.validation.year.bounds_check -> enforce business rule constraints
        if year < min_year:
            raise InvalidYearError(f"Movie year {year} is before first motion pictures ({min_year})")

        if year > max_year:
            raise InvalidYearError(f"Movie year {year} is too far in the future (max: {max_year})")

        # domain.movie.attribute.year -> store validated production year
        self._year: int = year

    def _validate_and_set_rating(self, rating: float) -> None:
        """
        Validate and set the movie rating.

        Args:
            rating: Proposed numeric rating

        Raises:
            InvalidRatingError: If rating is outside 1.0-10.0 range

        Domain.Movie.Validation.Rating -> business rule for rating scale bounds
        """
        # domain.validation.rating.bounds -> define acceptable rating range
        min_rating: float = 1.0
        max_rating: float = 10.0

        # domain.validation.rating.bounds_check -> enforce rating scale constraints
        if rating < min_rating or rating > max_rating:
            raise InvalidRatingError(
                f"Movie rating {rating} must be between {min_rating} and {max_rating}"
            )

        # domain.movie.attribute.rating -> store validated rating
        self._rating: float = rating

    @property
    def id(self) -> str:
        """
        Get the unique identifier for this movie.

        Returns:
            Unique string identifier for the movie entity

        Domain.Movie.Identity.Access -> immutable entity identifier
        """
        return self._id

    @property
    def title(self) -> str:
        """
        Get the movie title.

        Returns:
            Human-readable title string

        Domain.Movie.Content.Title_Access -> movie identification string
        """
        return self._title

    @property
    def year(self) -> int:
        """
        Get the movie production year.

        Returns:
            Integer year of movie production/release

        Domain.Movie.Metadata.Year_Access -> temporal classification
        """
        return self._year

    @property
    def description(self) -> str:
        """
        Get the movie description.

        Returns:
            Descriptive text about the movie content

        Domain.Movie.Content.Description_Access -> plot/synopsis information
        """
        return self._description

    @property
    def rating(self) -> Optional[float]:
        """
        Get the movie rating.

        Returns:
            Numeric rating (1.0-10.0) or None if unrated

        Domain.Movie.Evaluation.Rating_Access -> subjective quality assessment
        """
        return self._rating

    @property
    def tags(self) -> List[str]:
        """
        Get a copy of the movie tags.

        Returns:
            List of categorization strings (defensive copy)

        Domain.Movie.Classification.Tags_Access -> category collection
        """
        # domain.encapsulation.defensive_copy -> prevent external mutation
        return self._tags.copy()

    def rate(self, rating: float) -> None:
        """
        Set or update the movie rating.

        Args:
            rating: Numeric rating between 1.0 and 10.0

        Raises:
            InvalidRatingError: If rating is outside valid range

        Domain.Movie.Behavior.Rate -> business operation to assess movie quality
        """
        # domain.movie.mutation.rating_update -> modify evaluation after validation
        self._validate_and_set_rating(rating)

    def add_tag(self, tag: str) -> None:
        """
        Add a categorization tag to the movie.

        Args:
            tag: Category string to add to movie classification

        Domain.Movie.Behavior.Add_Tag -> business operation to categorize movie
        """
        # domain.movie.classification.tag_addition -> append new category
        if tag and tag.strip() and tag.strip() not in self._tags:
            # domain.movie.state.tags_collection -> maintain unique categorizations
            self._tags.append(tag.strip())

    def remove_tag(self, tag: str) -> None:
        """
        Remove a categorization tag from the movie.

        Args:
            tag: Category string to remove from movie classification

        Domain.Movie.Behavior.Remove_Tag -> business operation to uncategorize movie
        """
        # domain.movie.classification.tag_removal -> safe removal operation
        if tag in self._tags:
            # domain.movie.state.tags_modification -> update category collection
            self._tags.remove(tag)