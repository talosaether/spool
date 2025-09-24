"""
Test suite for movie command service.

This module tests the application layer command service that orchestrates
movie creation, modification, and deletion operations. The command service
sits between the domain layer and the adapters in our hexagonal architecture,
coordinating business operations while remaining technology-agnostic.
"""

import pytest
from unittest.mock import Mock, MagicMock
from movie_domain import Movie, InvalidRatingError, InvalidTitleError
from movie_repository import MovieRepository


class TestMovieCommandService:
    """Test cases for the MovieCommandService application service."""

    def test_command_service_requires_repository(self):
        """
        Test that command service requires repository dependency injection.

        Application.Service.Command.Dependencies -> repository injection required
        """
        from movie_command_service import MovieCommandService

        # application.service.dependency_injection -> repository required for construction
        mock_repository = Mock(spec=MovieRepository)
        service = MovieCommandService(mock_repository)

        # application.service.dependency.storage -> repository accessible via service
        assert service._repository is mock_repository

    def test_add_movie_with_valid_data(self):
        """
        Test adding a movie with valid data through command service.

        Application.Service.Command.Add_Movie -> create and persist movie entity
        """
        from movie_command_service import MovieCommandService

        # application.service.mock.repository -> mock storage dependency
        mock_repository = Mock(spec=MovieRepository)

        # application.service.instance -> create command service with mock
        service = MovieCommandService(mock_repository)

        # application.operation.add_movie -> create movie through service
        movie_data = {
            "title": "Test Movie",
            "year": 2023,
            "description": "A test movie description"
        }

        # application.service.command.add -> execute movie creation operation
        result_movie = service.add_movie(**movie_data)

        # application.service.verification.entity_created -> movie entity returned
        assert result_movie is not None
        assert result_movie.title == "Test Movie"
        assert result_movie.year == 2023
        assert result_movie.description == "A test movie description"

        # application.service.verification.repository_called -> persistence attempted
        mock_repository.save.assert_called_once_with(result_movie)

    def test_add_movie_with_rating_and_tags(self):
        """
        Test adding a movie with optional rating and tags.

        Application.Service.Command.Add_Movie_Complete -> create movie with all attributes
        """
        from movie_command_service import MovieCommandService

        # application.service.mock.repository -> mock storage dependency
        mock_repository = Mock(spec=MovieRepository)

        # application.service.instance -> create command service
        service = MovieCommandService(mock_repository)

        # application.operation.add_movie_complete -> create movie with all data
        movie_data = {
            "title": "Complete Movie",
            "year": 2023,
            "description": "Movie with rating and tags",
            "rating": 8.5,
            "tags": ["action", "thriller"]
        }

        # application.service.command.add_complete -> execute full movie creation
        result_movie = service.add_movie(**movie_data)

        # application.service.verification.complete_entity -> all attributes set
        assert result_movie.title == "Complete Movie"
        assert result_movie.rating == 8.5
        assert result_movie.tags == ["action", "thriller"]

        # application.service.verification.repository_persistence -> movie saved
        mock_repository.save.assert_called_once_with(result_movie)

    def test_add_movie_with_invalid_data_raises_domain_exception(self):
        """
        Test that invalid movie data raises appropriate domain exceptions.

        Application.Service.Command.Validation -> domain rules enforced through service
        """
        from movie_command_service import MovieCommandService

        # application.service.mock.repository -> mock storage dependency
        mock_repository = Mock(spec=MovieRepository)

        # application.service.instance -> create command service
        service = MovieCommandService(mock_repository)

        # application.service.validation.invalid_title -> domain exception propagated
        with pytest.raises(InvalidTitleError):
            service.add_movie(title="", year=2023, description="Test")

        # application.service.validation.invalid_rating -> domain exception propagated
        with pytest.raises(InvalidRatingError):
            service.add_movie(title="Test", year=2023, description="Test", rating=15.0)

        # application.service.verification.no_persistence -> invalid movies not saved
        mock_repository.save.assert_not_called()

    def test_rate_movie_success(self):
        """
        Test successfully rating an existing movie.

        Application.Service.Command.Rate_Movie -> update movie rating through service
        """
        from movie_command_service import MovieCommandService

        # application.service.test_data -> create existing movie
        existing_movie = Movie("Existing Movie", 2023, "Already exists")

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_id.return_value = existing_movie

        # application.service.instance -> create command service
        service = MovieCommandService(mock_repository)

        # application.service.command.rate -> execute rating operation
        result = service.rate_movie(existing_movie.id, 8.5)

        # application.service.verification.rating_success -> operation successful
        assert result is True

        # application.service.verification.movie_rated -> movie rating updated
        assert existing_movie.rating == 8.5

        # application.service.verification.repository_interactions -> proper calls made
        mock_repository.find_by_id.assert_called_once_with(existing_movie.id)
        mock_repository.save.assert_called_once_with(existing_movie)

    def test_rate_movie_not_found(self):
        """
        Test rating a movie that doesn't exist.

        Application.Service.Command.Rate_Movie_Missing -> handle nonexistent movie
        """
        from movie_command_service import MovieCommandService

        # application.service.mock.repository -> configure repository mock for missing movie
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_id.return_value = None

        # application.service.instance -> create command service
        service = MovieCommandService(mock_repository)

        # application.service.command.rate_missing -> attempt to rate nonexistent movie
        result = service.rate_movie("nonexistent-id", 8.5)

        # application.service.verification.rating_failure -> operation reports failure
        assert result is False

        # application.service.verification.repository_interactions -> only lookup attempted
        mock_repository.find_by_id.assert_called_once_with("nonexistent-id")
        mock_repository.save.assert_not_called()

    def test_rate_movie_invalid_rating(self):
        """
        Test rating a movie with invalid rating value.

        Application.Service.Command.Rate_Movie_Invalid -> domain validation enforced
        """
        from movie_command_service import MovieCommandService

        # application.service.test_data -> create existing movie
        existing_movie = Movie("Existing Movie", 2023, "Already exists")

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_id.return_value = existing_movie

        # application.service.instance -> create command service
        service = MovieCommandService(mock_repository)

        # application.service.validation.invalid_rating -> domain exception expected
        with pytest.raises(InvalidRatingError):
            service.rate_movie(existing_movie.id, 15.0)

        # application.service.verification.no_persistence -> invalid update not saved
        mock_repository.save.assert_not_called()

    def test_add_tag_to_movie_success(self):
        """
        Test successfully adding a tag to an existing movie.

        Application.Service.Command.Add_Tag -> modify movie tags through service
        """
        from movie_command_service import MovieCommandService

        # application.service.test_data -> create existing movie
        existing_movie = Movie("Existing Movie", 2023, "Already exists")

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_id.return_value = existing_movie

        # application.service.instance -> create command service
        service = MovieCommandService(mock_repository)

        # application.service.command.add_tag -> execute tag addition
        result = service.add_tag_to_movie(existing_movie.id, "action")

        # application.service.verification.tag_success -> operation successful
        assert result is True

        # application.service.verification.tag_added -> movie has new tag
        assert "action" in existing_movie.tags

        # application.service.verification.repository_interactions -> proper calls made
        mock_repository.find_by_id.assert_called_once_with(existing_movie.id)
        mock_repository.save.assert_called_once_with(existing_movie)

    def test_remove_tag_from_movie_success(self):
        """
        Test successfully removing a tag from an existing movie.

        Application.Service.Command.Remove_Tag -> modify movie tags through service
        """
        from movie_command_service import MovieCommandService

        # application.service.test_data -> create movie with existing tags
        existing_movie = Movie("Tagged Movie", 2023, "Has tags", tags=["action", "thriller"])

        # application.service.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_id.return_value = existing_movie

        # application.service.instance -> create command service
        service = MovieCommandService(mock_repository)

        # application.service.command.remove_tag -> execute tag removal
        result = service.remove_tag_from_movie(existing_movie.id, "action")

        # application.service.verification.tag_removal_success -> operation successful
        assert result is True

        # application.service.verification.tag_removed -> tag no longer present
        assert "action" not in existing_movie.tags
        assert "thriller" in existing_movie.tags  # Other tags preserved

        # application.service.verification.repository_interactions -> proper calls made
        mock_repository.find_by_id.assert_called_once_with(existing_movie.id)
        mock_repository.save.assert_called_once_with(existing_movie)

    def test_delete_movie_success(self):
        """
        Test successfully deleting an existing movie.

        Application.Service.Command.Delete_Movie -> remove movie through service
        """
        from movie_command_service import MovieCommandService

        # application.service.mock.repository -> configure repository mock for successful deletion
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.delete.return_value = True

        # application.service.instance -> create command service
        service = MovieCommandService(mock_repository)

        # application.service.command.delete -> execute movie deletion
        result = service.delete_movie("existing-movie-id")

        # application.service.verification.delete_success -> operation successful
        assert result is True

        # application.service.verification.repository_interaction -> deletion attempted
        mock_repository.delete.assert_called_once_with("existing-movie-id")

    def test_delete_movie_not_found(self):
        """
        Test deleting a movie that doesn't exist.

        Application.Service.Command.Delete_Movie_Missing -> handle nonexistent movie
        """
        from movie_command_service import MovieCommandService

        # application.service.mock.repository -> configure repository mock for missing movie
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.delete.return_value = False

        # application.service.instance -> create command service
        service = MovieCommandService(mock_repository)

        # application.service.command.delete_missing -> attempt to delete nonexistent movie
        result = service.delete_movie("nonexistent-id")

        # application.service.verification.delete_failure -> operation reports failure
        assert result is False

        # application.service.verification.repository_interaction -> deletion attempted
        mock_repository.delete.assert_called_once_with("nonexistent-id")

    def test_command_service_repository_error_handling(self):
        """
        Test that command service handles repository errors appropriately.

        Application.Service.Command.Error_Handling -> infrastructure failure handling
        """
        from movie_command_service import MovieCommandService

        # application.service.mock.repository -> configure repository to raise exception
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.save.side_effect = Exception("Storage error")

        # application.service.instance -> create command service
        service = MovieCommandService(mock_repository)

        # application.service.error.storage_failure -> repository exception propagated
        with pytest.raises(Exception) as exc_info:
            service.add_movie("Test Movie", 2023, "Test description")

        # application.service.verification.error_details -> correct exception propagated
        assert str(exc_info.value) == "Storage error"