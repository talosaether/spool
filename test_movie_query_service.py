"""
Test suite for movie query service.

This module tests the application layer query service that handles all
read-only operations for movies. The query service provides sophisticated
search and filtering capabilities while maintaining separation from
command operations in our CQRS-influenced hexagonal architecture.
"""

import pytest
from unittest.mock import Mock, MagicMock
from movie_domain import Movie
from movie_repository import MovieRepository, MovieFilters, InvalidFilterError


class TestMovieQueryService:
    """Test cases for the MovieQueryService application service."""

    def test_query_service_requires_repository(self):
        """
        Test that query service requires repository dependency injection.

        Application.Service.Query.Dependencies -> repository injection required
        """
        from movie_query_service import MovieQueryService

        # application.service.dependency_injection -> repository required for construction
        mock_repository = Mock(spec=MovieRepository)
        service = MovieQueryService(mock_repository)

        # application.service.dependency.storage -> repository accessible via service
        assert service._repository is mock_repository

    def test_get_all_movies(self):
        """
        Test retrieving all movies from the catalog.

        Application.Service.Query.Get_All -> retrieve complete movie collection
        """
        from movie_query_service import MovieQueryService

        # application.service.test_data -> create sample movies
        movie1 = Movie("Movie One", 2021, "First movie")
        movie2 = Movie("Movie Two", 2022, "Second movie")
        expected_movies = [movie1, movie2]

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_all.return_value = expected_movies

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.query.all -> execute complete retrieval operation
        result_movies = service.get_all_movies()

        # application.service.verification.complete_collection -> all movies returned
        assert result_movies == expected_movies
        assert len(result_movies) == 2

        # application.service.verification.repository_interaction -> repository called
        mock_repository.find_all.assert_called_once()

    def test_get_movie_by_id_found(self):
        """
        Test retrieving a specific movie by its identifier.

        Application.Service.Query.Get_By_Id -> retrieve single movie by identity
        """
        from movie_query_service import MovieQueryService

        # application.service.test_data -> create sample movie
        target_movie = Movie("Target Movie", 2023, "The movie we want")

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_id.return_value = target_movie

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.query.by_id -> execute retrieval by identifier
        result_movie = service.get_movie_by_id(target_movie.id)

        # application.service.verification.single_movie -> correct movie returned
        assert result_movie == target_movie
        assert result_movie.title == "Target Movie"

        # application.service.verification.repository_interaction -> repository called with ID
        mock_repository.find_by_id.assert_called_once_with(target_movie.id)

    def test_get_movie_by_id_not_found(self):
        """
        Test retrieving a movie by ID when it doesn't exist.

        Application.Service.Query.Get_By_Id_Missing -> handle nonexistent movie
        """
        from movie_query_service import MovieQueryService

        # application.service.mock.repository -> configure repository mock for missing movie
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_id.return_value = None

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.query.by_id_missing -> attempt to retrieve nonexistent movie
        result_movie = service.get_movie_by_id("nonexistent-id")

        # application.service.verification.not_found -> None returned for missing movie
        assert result_movie is None

        # application.service.verification.repository_interaction -> repository called
        mock_repository.find_by_id.assert_called_once_with("nonexistent-id")

    def test_search_movies_by_title(self):
        """
        Test searching movies by title substring.

        Application.Service.Query.Search_Title -> text-based movie search
        """
        from movie_query_service import MovieQueryService

        # application.service.test_data -> create sample search results
        matching_movies = [
            Movie("The Matrix", 1999, "Sci-fi classic"),
            Movie("Matrix Reloaded", 2003, "The sequel")
        ]

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_filters.return_value = matching_movies

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.query.search_title -> execute title search
        search_term = "Matrix"
        result_movies = service.search_movies_by_title(search_term)

        # application.service.verification.search_results -> matching movies returned
        assert result_movies == matching_movies
        assert len(result_movies) == 2

        # application.service.verification.repository_interaction -> correct filter applied
        mock_repository.find_by_filters.assert_called_once_with(title=search_term)

    def test_get_movies_by_year(self):
        """
        Test filtering movies by specific release year.

        Application.Service.Query.Filter_Year -> temporal filtering operation
        """
        from movie_query_service import MovieQueryService

        # application.service.test_data -> create sample filtered results
        movies_2021 = [
            Movie("Movie A", 2021, "From 2021"),
            Movie("Movie B", 2021, "Also from 2021")
        ]

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_filters.return_value = movies_2021

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.query.filter_year -> execute year filtering
        target_year = 2021
        result_movies = service.get_movies_by_year(target_year)

        # application.service.verification.filter_results -> correct movies returned
        assert result_movies == movies_2021
        assert len(result_movies) == 2

        # application.service.verification.repository_interaction -> correct filter applied
        mock_repository.find_by_filters.assert_called_once_with(year=target_year)

    def test_get_movies_by_rating_range(self):
        """
        Test filtering movies by rating range.

        Application.Service.Query.Filter_Rating -> numeric range filtering operation
        """
        from movie_query_service import MovieQueryService

        # application.service.test_data -> create sample rated movies
        highly_rated_movies = [
            Movie("Great Movie", 2022, "Excellent film", rating=9.0),
            Movie("Good Movie", 2023, "Pretty good", rating=8.5)
        ]

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_filters.return_value = highly_rated_movies

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.query.filter_rating_range -> execute rating filtering
        min_rating = 8.0
        max_rating = 10.0
        result_movies = service.get_movies_by_rating_range(min_rating, max_rating)

        # application.service.verification.rating_filter_results -> correct movies returned
        assert result_movies == highly_rated_movies
        assert len(result_movies) == 2

        # application.service.verification.repository_interaction -> correct filter applied
        mock_repository.find_by_filters.assert_called_once_with(
            rating_min=min_rating,
            rating_max=max_rating
        )

    def test_get_movies_by_tags(self):
        """
        Test filtering movies by required tags.

        Application.Service.Query.Filter_Tags -> category-based filtering operation
        """
        from movie_query_service import MovieQueryService

        # application.service.test_data -> create sample tagged movies
        scifi_movies = [
            Movie("Sci-Fi Movie", 2022, "Space adventure", tags=["sci-fi", "adventure"]),
            Movie("Another Sci-Fi", 2023, "More space", tags=["sci-fi", "drama"])
        ]

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_filters.return_value = scifi_movies

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.query.filter_tags -> execute tag filtering
        required_tags = ["sci-fi"]
        result_movies = service.get_movies_by_tags(required_tags)

        # application.service.verification.tag_filter_results -> correct movies returned
        assert result_movies == scifi_movies
        assert len(result_movies) == 2

        # application.service.verification.repository_interaction -> correct filter applied
        mock_repository.find_by_filters.assert_called_once_with(tags=required_tags)

    def test_search_movies_with_filters(self):
        """
        Test comprehensive movie search with multiple filter criteria.

        Application.Service.Query.Search_Complex -> multi-criteria filtering operation
        """
        from movie_query_service import MovieQueryService

        # application.service.test_data -> create sample complex search results
        filtered_movies = [
            Movie("Perfect Match", 2022, "Matches all criteria", rating=9.0, tags=["action"])
        ]

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_filters.return_value = filtered_movies

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.query.complex_search -> execute multi-criteria search
        search_criteria = {
            "title": "Perfect",
            "year": 2022,
            "rating_min": 8.0,
            "rating_max": 10.0,
            "tags": ["action"]
        }
        result_movies = service.search_movies(**search_criteria)

        # application.service.verification.complex_search_results -> matching movies returned
        assert result_movies == filtered_movies
        assert len(result_movies) == 1

        # application.service.verification.repository_interaction -> all filters applied
        mock_repository.find_by_filters.assert_called_once_with(**search_criteria)

    def test_get_movie_count(self):
        """
        Test getting the total count of movies in the catalog.

        Application.Service.Query.Count -> collection size operation
        """
        from movie_query_service import MovieQueryService

        # application.service.mock.repository -> configure repository mock
        expected_count = 42
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.count.return_value = expected_count

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.query.count -> execute count operation
        result_count = service.get_movie_count()

        # application.service.verification.count_result -> correct count returned
        assert result_count == expected_count

        # application.service.verification.repository_interaction -> repository called
        mock_repository.count.assert_called_once()

    def test_search_movies_with_invalid_filters_raises_exception(self):
        """
        Test that invalid filter criteria raise appropriate exceptions.

        Application.Service.Query.Validation -> filter validation and error handling
        """
        from movie_query_service import MovieQueryService

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_filters.side_effect = InvalidFilterError("Invalid rating range")

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.validation.invalid_filters -> filter exception propagated
        with pytest.raises(InvalidFilterError) as exc_info:
            service.search_movies(rating_min=10.0, rating_max=5.0)

        # application.service.verification.error_details -> correct exception propagated
        assert "Invalid rating range" in str(exc_info.value)

    def test_get_movies_statistics(self):
        """
        Test getting statistical information about the movie catalog.

        Application.Service.Query.Statistics -> aggregate information operation
        """
        from movie_query_service import MovieQueryService

        # application.service.test_data -> create sample movies for statistics
        sample_movies = [
            Movie("Movie 1", 2020, "Description 1", rating=8.0, tags=["action"]),
            Movie("Movie 2", 2021, "Description 2", rating=7.5, tags=["drama"]),
            Movie("Movie 3", 2022, "Description 3", rating=9.0, tags=["action", "thriller"])
        ]

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_all.return_value = sample_movies
        mock_repository.count.return_value = len(sample_movies)

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.query.statistics -> execute statistics calculation
        stats = service.get_catalog_statistics()

        # application.service.verification.statistics_content -> correct statistics returned
        assert stats["total_movies"] == 3
        assert stats["average_rating"] == 8.17  # (8.0 + 7.5 + 9.0) / 3 = 8.17 (rounded)
        assert stats["movies_with_ratings"] == 3
        assert stats["unique_tags"] == {"action", "drama", "thriller"}

        # application.service.verification.repository_interactions -> proper calls made
        mock_repository.find_all.assert_called_once()
        mock_repository.count.assert_called_once()

    def test_query_service_repository_error_handling(self):
        """
        Test that query service handles repository errors appropriately.

        Application.Service.Query.Error_Handling -> infrastructure failure handling
        """
        from movie_query_service import MovieQueryService

        # application.service.mock.repository -> configure repository to raise exception
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_all.side_effect = Exception("Storage connection error")

        # application.service.instance -> create query service
        service = MovieQueryService(mock_repository)

        # application.service.error.storage_failure -> repository exception propagated
        with pytest.raises(Exception) as exc_info:
            service.get_all_movies()

        # application.service.verification.error_details -> correct exception propagated
        assert str(exc_info.value) == "Storage connection error"