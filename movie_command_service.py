"""
Movie command service for the application layer.

This module provides the command service that orchestrates movie creation,
modification, and deletion operations in our hexagonal architecture.
It coordinates between the domain layer and repository adapters while
maintaining separation of concerns and enforcing business rules.

Application layer responsibilities:
- Orchestrate complex business operations
- Coordinate domain entities and repository interactions
- Provide transaction boundaries
- Handle application-specific logic and workflows
"""

from typing import List, Optional
from movie_domain import Movie
from movie_repository import MovieRepository


class MovieCommandService:
    """
    Application service for movie command operations.

    This service handles all operations that modify the state of movies
    in our catalog system. It orchestrates interactions between domain
    entities and the repository while enforcing business rules and
    maintaining data consistency.

    Application.Service.Command -> state modification operations coordinator
    """

    def __init__(self, repository: MovieRepository):
        """
        Initialize command service with repository dependency.

        Args:
            repository: MovieRepository implementation for persistence operations

        Application.Service.Construction -> dependency injection for storage abstraction
        """
        # application.service.dependency.repository -> injected storage abstraction
        self._repository: MovieRepository = repository

    def add_movie(
        self,
        title: str,
        year: int,
        description: str,
        rating: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> Movie:
        """
        Create and persist a new movie entity.

        This operation creates a new movie with the provided attributes,
        validates it according to domain rules, and persists it to storage.
        All domain validation is handled by the Movie entity constructor.

        Args:
            title: Human-readable movie title
            year: Release year for the movie
            description: Plot synopsis or movie description
            rating: Optional numeric rating (1.0-10.0)
            tags: Optional list of categorization strings

        Returns:
            The created and persisted Movie entity

        Raises:
            InvalidTitleError: If title is empty or invalid
            InvalidYearError: If year is outside reasonable bounds
            InvalidRatingError: If rating is outside valid range
            Repository exceptions: If persistence fails

        Application.Service.Command.Add_Movie -> create and persist new movie entity
        """
        # application.operation.entity_creation -> delegate validation to domain
        movie = Movie(
            title=title,
            year=year,
            description=description,
            rating=rating,
            tags=tags
        )

        # application.operation.persistence -> save entity through repository abstraction
        self._repository.save(movie)

        # application.service.result.created_entity -> return persisted entity
        return movie

    def rate_movie(self, movie_id: str, rating: float) -> bool:
        """
        Update the rating of an existing movie.

        This operation retrieves the specified movie, updates its rating
        according to domain rules, and persists the changes. The rating
        validation is handled by the Movie entity's rate method.

        Args:
            movie_id: Unique identifier for the movie to rate
            rating: Numeric rating between 1.0 and 10.0

        Returns:
            True if movie was found and rating updated successfully, False if movie not found

        Raises:
            InvalidRatingError: If rating is outside valid range
            Repository exceptions: If retrieval or persistence fails

        Application.Service.Command.Rate_Movie -> update existing movie rating
        """
        # application.operation.retrieval -> find target movie entity
        movie = self._repository.find_by_id(movie_id)

        # application.logic.existence_check -> verify movie exists before modification
        if movie is None:
            # application.service.result.not_found -> indicate target not found
            return False

        # application.operation.domain_update -> delegate rating logic to domain entity
        movie.rate(rating)

        # application.operation.persistence -> save modified entity
        self._repository.save(movie)

        # application.service.result.success -> indicate successful operation
        return True

    def add_tag_to_movie(self, movie_id: str, tag: str) -> bool:
        """
        Add a categorization tag to an existing movie.

        This operation retrieves the specified movie, adds the provided tag
        using domain logic, and persists the changes. Tag validation and
        duplicate prevention are handled by the Movie entity.

        Args:
            movie_id: Unique identifier for the movie to tag
            tag: Categorization string to add to the movie

        Returns:
            True if movie was found and tag added successfully, False if movie not found

        Raises:
            Repository exceptions: If retrieval or persistence fails

        Application.Service.Command.Add_Tag -> add categorization to existing movie
        """
        # application.operation.retrieval -> find target movie entity
        movie = self._repository.find_by_id(movie_id)

        # application.logic.existence_check -> verify movie exists before modification
        if movie is None:
            # application.service.result.not_found -> indicate target not found
            return False

        # application.operation.domain_update -> delegate tag logic to domain entity
        movie.add_tag(tag)

        # application.operation.persistence -> save modified entity
        self._repository.save(movie)

        # application.service.result.success -> indicate successful operation
        return True

    def remove_tag_from_movie(self, movie_id: str, tag: str) -> bool:
        """
        Remove a categorization tag from an existing movie.

        This operation retrieves the specified movie, removes the provided tag
        using domain logic, and persists the changes. Safe removal (no error
        if tag doesn't exist) is handled by the Movie entity.

        Args:
            movie_id: Unique identifier for the movie to untag
            tag: Categorization string to remove from the movie

        Returns:
            True if movie was found and tag removal attempted, False if movie not found

        Raises:
            Repository exceptions: If retrieval or persistence fails

        Application.Service.Command.Remove_Tag -> remove categorization from existing movie
        """
        # application.operation.retrieval -> find target movie entity
        movie = self._repository.find_by_id(movie_id)

        # application.logic.existence_check -> verify movie exists before modification
        if movie is None:
            # application.service.result.not_found -> indicate target not found
            return False

        # application.operation.domain_update -> delegate tag removal logic to domain entity
        movie.remove_tag(tag)

        # application.operation.persistence -> save modified entity
        self._repository.save(movie)

        # application.service.result.success -> indicate successful operation
        return True

    def delete_movie(self, movie_id: str) -> bool:
        """
        Delete an existing movie from the catalog.

        This operation removes the specified movie from persistent storage.
        The actual deletion logic and existence checking are handled by
        the repository implementation.

        Args:
            movie_id: Unique identifier for the movie to delete

        Returns:
            True if movie was found and deleted successfully, False if movie not found

        Raises:
            Repository exceptions: If deletion operation fails

        Application.Service.Command.Delete_Movie -> remove movie from catalog
        """
        # application.operation.deletion -> delegate removal to repository
        deletion_result = self._repository.delete(movie_id)

        # application.service.result.deletion_outcome -> return repository result
        return deletion_result