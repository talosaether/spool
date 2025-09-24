"""
Test suite for movie repository port interface.

This module tests the abstract repository interface that defines the contract
between our domain layer and storage adapters in the hexagonal architecture.
The repository port enables dependency inversion - domain depends on abstraction,
not concrete storage implementation.
"""

import pytest
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

# Test will drive the creation of our repository port interface


class TestMovieRepositoryInterface:
    """Test cases for the MovieRepository port interface."""

    def test_repository_is_abstract_base_class(self):
        """
        Test that MovieRepository is properly defined as an abstract interface.

        Domain.Port.Repository.Abstraction -> interface contract for storage
        """
        from movie_repository import MovieRepository

        # domain.port.repository.abstract_nature -> cannot instantiate directly
        with pytest.raises(TypeError):
            MovieRepository()

    def test_repository_defines_save_method(self):
        """
        Test that repository interface defines save method contract.

        Domain.Port.Repository.Save -> persistence operation contract
        """
        from movie_repository import MovieRepository
        from movie_domain import Movie
        import inspect

        # domain.port.repository.method.save -> required abstract method
        assert hasattr(MovieRepository, 'save')
        save_method = getattr(MovieRepository, 'save')

        # domain.interface.method.abstract_check -> method must be abstract
        assert getattr(save_method, '__isabstractmethod__', False)

        # domain.interface.signature.save -> expected parameter and return types
        signature = inspect.signature(save_method)
        assert 'movie' in signature.parameters

    def test_repository_defines_find_by_id_method(self):
        """
        Test that repository interface defines find_by_id method contract.

        Domain.Port.Repository.Find_By_Id -> retrieval by unique identifier
        """
        from movie_repository import MovieRepository
        import inspect

        # domain.port.repository.method.find_by_id -> required abstract method
        assert hasattr(MovieRepository, 'find_by_id')
        find_method = getattr(MovieRepository, 'find_by_id')

        # domain.interface.method.abstract_check -> method must be abstract
        assert getattr(find_method, '__isabstractmethod__', False)

        # domain.interface.signature.find_by_id -> expected parameter types
        signature = inspect.signature(find_method)
        assert 'movie_id' in signature.parameters

    def test_repository_defines_find_all_method(self):
        """
        Test that repository interface defines find_all method contract.

        Domain.Port.Repository.Find_All -> retrieve all stored movies
        """
        from movie_repository import MovieRepository
        import inspect

        # domain.port.repository.method.find_all -> required abstract method
        assert hasattr(MovieRepository, 'find_all')
        find_all_method = getattr(MovieRepository, 'find_all')

        # domain.interface.method.abstract_check -> method must be abstract
        assert getattr(find_all_method, '__isabstractmethod__', False)

    def test_repository_defines_find_by_filters_method(self):
        """
        Test that repository interface defines filtering method contract.

        Domain.Port.Repository.Find_By_Filters -> search and filter operations
        """
        from movie_repository import MovieRepository
        import inspect

        # domain.port.repository.method.find_by_filters -> required abstract method
        assert hasattr(MovieRepository, 'find_by_filters')
        filter_method = getattr(MovieRepository, 'find_by_filters')

        # domain.interface.method.abstract_check -> method must be abstract
        assert getattr(filter_method, '__isabstractmethod__', False)

        # domain.interface.signature.find_by_filters -> expected parameter types
        signature = inspect.signature(filter_method)
        # domain.port.repository.filter.parameters -> flexible filter criteria
        parameter_names = list(signature.parameters.keys())
        expected_params = ['title', 'year', 'rating_min', 'rating_max', 'tags']

        # domain.interface.contract.filter_params -> all filter options available
        for param in expected_params:
            assert param in parameter_names, f"Missing filter parameter: {param}"

    def test_repository_defines_delete_method(self):
        """
        Test that repository interface defines delete method contract.

        Domain.Port.Repository.Delete -> removal operation contract
        """
        from movie_repository import MovieRepository
        import inspect

        # domain.port.repository.method.delete -> required abstract method
        assert hasattr(MovieRepository, 'delete')
        delete_method = getattr(MovieRepository, 'delete')

        # domain.interface.method.abstract_check -> method must be abstract
        assert getattr(delete_method, '__isabstractmethod__', False)

        # domain.interface.signature.delete -> expected parameter types
        signature = inspect.signature(delete_method)
        assert 'movie_id' in signature.parameters

    def test_repository_defines_count_method(self):
        """
        Test that repository interface defines count method contract.

        Domain.Port.Repository.Count -> collection size operation
        """
        from movie_repository import MovieRepository
        import inspect

        # domain.port.repository.method.count -> required abstract method
        assert hasattr(MovieRepository, 'count')
        count_method = getattr(MovieRepository, 'count')

        # domain.interface.method.abstract_check -> method must be abstract
        assert getattr(count_method, '__isabstractmethod__', False)


class TestMovieFilters:
    """Test cases for the MovieFilters value object."""

    def test_movie_filters_creation_empty(self):
        """
        Test creating empty filter criteria.

        Domain.ValueObject.MovieFilters.Empty -> no filtering criteria
        """
        from movie_repository import MovieFilters

        # domain.filters.creation.empty -> default no-filter state
        filters = MovieFilters()

        # domain.filters.state.empty_check -> all criteria should be None/empty
        assert filters.title is None
        assert filters.year is None
        assert filters.rating_min is None
        assert filters.rating_max is None
        assert filters.tags == []

    def test_movie_filters_creation_with_title(self):
        """
        Test creating filter with title search criteria.

        Domain.ValueObject.MovieFilters.Title -> text-based filtering
        """
        from movie_repository import MovieFilters

        # domain.filters.creation.title_search -> partial title matching criteria
        filters = MovieFilters(title="Matrix")

        # domain.filters.state.title_criterion -> title filter populated
        assert filters.title == "Matrix"
        # domain.filters.state.other_criteria -> other filters remain empty
        assert filters.year is None
        assert filters.rating_min is None

    def test_movie_filters_creation_with_rating_range(self):
        """
        Test creating filter with rating range criteria.

        Domain.ValueObject.MovieFilters.Rating_Range -> numeric range filtering
        """
        from movie_repository import MovieFilters

        # domain.filters.creation.rating_range -> min/max rating bounds
        filters = MovieFilters(rating_min=7.0, rating_max=10.0)

        # domain.filters.state.rating_bounds -> rating range populated
        assert filters.rating_min == 7.0
        assert filters.rating_max == 10.0

    def test_movie_filters_creation_with_tags(self):
        """
        Test creating filter with tag criteria.

        Domain.ValueObject.MovieFilters.Tags -> category-based filtering
        """
        from movie_repository import MovieFilters

        # domain.filters.creation.tags_list -> collection of required categories
        tag_criteria = ["sci-fi", "action"]
        filters = MovieFilters(tags=tag_criteria)

        # domain.filters.state.tags_criteria -> tag list populated
        assert filters.tags == ["sci-fi", "action"]

    def test_movie_filters_is_empty(self):
        """
        Test the is_empty method to detect no filtering criteria.

        Domain.ValueObject.MovieFilters.Empty_Check -> detect no-filter state
        """
        from movie_repository import MovieFilters

        # domain.filters.behavior.empty_detection -> method to check no criteria
        empty_filters = MovieFilters()
        assert empty_filters.is_empty() is True

        # domain.filters.behavior.non_empty_detection -> method detects criteria
        title_filters = MovieFilters(title="Test")
        assert title_filters.is_empty() is False

        rating_filters = MovieFilters(rating_min=5.0)
        assert rating_filters.is_empty() is False

        tag_filters = MovieFilters(tags=["drama"])
        assert tag_filters.is_empty() is False

    def test_movie_filters_validation_rating_range(self):
        """
        Test that rating range validation works correctly.

        Domain.ValueObject.MovieFilters.Validation -> business rule enforcement
        """
        from movie_repository import MovieFilters, InvalidFilterError

        # domain.filters.validation.rating_range -> min cannot exceed max
        with pytest.raises(InvalidFilterError):
            MovieFilters(rating_min=8.0, rating_max=6.0)

        # domain.filters.validation.rating_bounds -> ratings within valid range
        with pytest.raises(InvalidFilterError):
            MovieFilters(rating_min=0.5)  # Below minimum rating

        with pytest.raises(InvalidFilterError):
            MovieFilters(rating_max=11.0)  # Above maximum rating

        # domain.filters.validation.valid_range -> acceptable rating ranges
        valid_filters = MovieFilters(rating_min=1.0, rating_max=10.0)
        assert valid_filters.rating_min == 1.0
        assert valid_filters.rating_max == 10.0