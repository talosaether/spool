"""
Test suite for Flask web adapter.

This module tests the Flask web adapter that provides REST API endpoints
for movie catalog operations. The web adapter should provide the same
functionality as the CLI adapter, demonstrating hexagonal architecture's
ability to support multiple driving adapters.
"""

import pytest
import json
from unittest.mock import Mock
from movie_domain import Movie
from movie_repository import MovieRepository
from in_memory_repository import InMemoryMovieRepository


class TestMovieWebAdapter:
    """Test cases for the Flask web adapter."""

    def test_flask_app_creation(self):
        """
        Test that Flask app can be created with repository injection.

        Adapter.Web.Flask.Creation -> web adapter instantiation with dependencies
        """
        from movie_web_adapter import create_app

        # adapter.web.mock.repository -> mock storage dependency
        mock_repository = Mock(spec=MovieRepository)

        # adapter.web.creation -> create Flask application
        app = create_app(mock_repository)

        # adapter.web.verification.app_created -> Flask app instance created
        assert app is not None
        assert hasattr(app, 'test_client')

    def test_get_movies_empty_catalog(self):
        """
        Test GET /movies endpoint with empty catalog.

        Adapter.Web.Endpoint.Get_Movies_Empty -> handle empty collection
        """
        from movie_web_adapter import create_app

        # adapter.web.mock.repository -> configure empty repository
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_all.return_value = []

        # adapter.web.test.setup -> create test client
        app = create_app(mock_repository)
        client = app.test_client()

        # adapter.web.request.get_movies -> execute GET request
        response = client.get('/movies')

        # adapter.web.verification.empty_response -> correct empty response
        assert response.status_code == 200
        assert response.content_type.startswith('application/json')

        data = json.loads(response.data)
        assert data == []

        # adapter.web.verification.repository_interaction -> repository called
        mock_repository.find_all.assert_called_once()

    def test_get_movies_with_data(self):
        """
        Test GET /movies endpoint with movie data.

        Adapter.Web.Endpoint.Get_Movies_Data -> return movie collection
        """
        from movie_web_adapter import create_app

        # adapter.web.test_data -> create sample movies
        movie1 = Movie("Test Movie 1", 2021, "First movie", rating=8.0, tags=["action"])
        movie2 = Movie("Test Movie 2", 2022, "Second movie", tags=["drama"])
        sample_movies = [movie1, movie2]

        # adapter.web.mock.repository -> configure repository with data
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_all.return_value = sample_movies

        # adapter.web.test.setup -> create test client
        app = create_app(mock_repository)
        client = app.test_client()

        # adapter.web.request.get_movies -> execute GET request
        response = client.get('/movies')

        # adapter.web.verification.data_response -> correct movie data returned
        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data) == 2
        assert data[0]['title'] == "Test Movie 1"
        assert data[0]['rating'] == 8.0
        assert data[0]['tags'] == ["action"]
        assert data[1]['title'] == "Test Movie 2"
        assert data[1]['rating'] is None
        assert data[1]['tags'] == ["drama"]

    def test_post_movie_valid_data(self):
        """
        Test POST /movies endpoint with valid movie data.

        Adapter.Web.Endpoint.Post_Movie_Valid -> create movie via API
        """
        from movie_web_adapter import create_app

        # adapter.web.mock.repository -> mock storage dependency
        mock_repository = Mock(spec=MovieRepository)

        # adapter.web.test.setup -> create test client
        app = create_app(mock_repository)
        client = app.test_client()

        # adapter.web.request_data -> movie creation payload
        movie_data = {
            "title": "New Movie",
            "year": 2023,
            "description": "A new movie",
            "rating": 7.5,
            "tags": ["comedy", "romance"]
        }

        # adapter.web.request.post_movie -> execute POST request
        response = client.post('/movies',
                              data=json.dumps(movie_data),
                              content_type='application/json')

        # adapter.web.verification.creation_response -> movie created successfully
        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['title'] == "New Movie"
        assert data['year'] == 2023
        assert data['rating'] == 7.5
        assert data['tags'] == ["comedy", "romance"]
        assert 'id' in data

        # adapter.web.verification.repository_interaction -> movie saved
        mock_repository.save.assert_called_once()

    def test_post_movie_invalid_data(self):
        """
        Test POST /movies endpoint with invalid movie data.

        Adapter.Web.Endpoint.Post_Movie_Invalid -> handle validation errors
        """
        from movie_web_adapter import create_app

        # adapter.web.mock.repository -> mock storage dependency
        mock_repository = Mock(spec=MovieRepository)

        # adapter.web.test.setup -> create test client
        app = create_app(mock_repository)
        client = app.test_client()

        # adapter.web.request_data.invalid -> invalid movie payload
        invalid_data = {
            "title": "",  # Invalid empty title
            "year": 2023,
            "description": "Test description"
        }

        # adapter.web.request.post_invalid -> execute POST with invalid data
        response = client.post('/movies',
                              data=json.dumps(invalid_data),
                              content_type='application/json')

        # adapter.web.verification.validation_error -> proper error response
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

        # adapter.web.verification.no_persistence -> invalid movie not saved
        mock_repository.save.assert_not_called()

    def test_get_movie_by_id_found(self):
        """
        Test GET /movies/<id> endpoint for existing movie.

        Adapter.Web.Endpoint.Get_Movie_By_Id_Found -> retrieve single movie
        """
        from movie_web_adapter import create_app

        # adapter.web.test_data -> create sample movie
        target_movie = Movie("Target Movie", 2023, "The movie we want", rating=8.5)

        # adapter.web.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_id.return_value = target_movie

        # adapter.web.test.setup -> create test client
        app = create_app(mock_repository)
        client = app.test_client()

        # adapter.web.request.get_by_id -> execute GET request with ID
        response = client.get(f'/movies/{target_movie.id}')

        # adapter.web.verification.single_movie_response -> correct movie returned
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['id'] == target_movie.id
        assert data['title'] == "Target Movie"
        assert data['rating'] == 8.5

        # adapter.web.verification.repository_interaction -> repository called with ID
        mock_repository.find_by_id.assert_called_once_with(target_movie.id)

    def test_get_movie_by_id_not_found(self):
        """
        Test GET /movies/<id> endpoint for nonexistent movie.

        Adapter.Web.Endpoint.Get_Movie_By_Id_Not_Found -> handle missing movie
        """
        from movie_web_adapter import create_app

        # adapter.web.mock.repository -> configure repository for missing movie
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_id.return_value = None

        # adapter.web.test.setup -> create test client
        app = create_app(mock_repository)
        client = app.test_client()

        # adapter.web.request.get_missing -> execute GET for nonexistent ID
        response = client.get('/movies/nonexistent-id')

        # adapter.web.verification.not_found_response -> 404 error returned
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_put_movie_rating(self):
        """
        Test PUT /movies/<id>/rating endpoint.

        Adapter.Web.Endpoint.Put_Rating -> update movie rating via API
        """
        from movie_web_adapter import create_app

        # adapter.web.test_data -> create existing movie
        existing_movie = Movie("Existing Movie", 2023, "Already exists")

        # adapter.web.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_id.return_value = existing_movie

        # adapter.web.test.setup -> create test client
        app = create_app(mock_repository)
        client = app.test_client()

        # adapter.web.request_data -> rating update payload
        rating_data = {"rating": 9.0}

        # adapter.web.request.put_rating -> execute PUT request
        response = client.put(f'/movies/{existing_movie.id}/rating',
                             data=json.dumps(rating_data),
                             content_type='application/json')

        # adapter.web.verification.rating_update -> rating updated successfully
        assert response.status_code == 200
        assert existing_movie.rating == 9.0

        # adapter.web.verification.repository_interactions -> proper calls made
        mock_repository.find_by_id.assert_called_once_with(existing_movie.id)
        mock_repository.save.assert_called_once_with(existing_movie)

    def test_delete_movie(self):
        """
        Test DELETE /movies/<id> endpoint.

        Adapter.Web.Endpoint.Delete_Movie -> remove movie via API
        """
        from movie_web_adapter import create_app

        # adapter.web.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.delete.return_value = True

        # adapter.web.test.setup -> create test client
        app = create_app(mock_repository)
        client = app.test_client()

        # adapter.web.request.delete -> execute DELETE request
        response = client.delete('/movies/test-movie-id')

        # adapter.web.verification.deletion_response -> successful deletion
        assert response.status_code == 204

        # adapter.web.verification.repository_interaction -> deletion attempted
        mock_repository.delete.assert_called_once_with('test-movie-id')

    def test_get_movies_with_filters(self):
        """
        Test GET /movies with query parameters for filtering.

        Adapter.Web.Endpoint.Get_Movies_Filtered -> search with query params
        """
        from movie_web_adapter import create_app

        # adapter.web.test_data -> create filtered results
        filtered_movies = [
            Movie("Sci-Fi Movie", 2022, "Space adventure", rating=8.5, tags=["sci-fi"])
        ]

        # adapter.web.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_by_filters.return_value = filtered_movies

        # adapter.web.test.setup -> create test client
        app = create_app(mock_repository)
        client = app.test_client()

        # adapter.web.request.get_filtered -> execute GET with query parameters
        response = client.get('/movies?title=Sci-Fi&min_rating=8.0&tags=sci-fi')

        # adapter.web.verification.filtered_response -> correct filtered results
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['title'] == "Sci-Fi Movie"

        # adapter.web.verification.repository_interaction -> filters applied
        mock_repository.find_by_filters.assert_called_once_with(
            title="Sci-Fi",
            year=None,
            rating_min=8.0,
            rating_max=None,
            tags=["sci-fi"]
        )

    def test_get_statistics_endpoint(self):
        """
        Test GET /statistics endpoint.

        Adapter.Web.Endpoint.Get_Statistics -> catalog statistics via API
        """
        from movie_web_adapter import create_app

        # adapter.web.test_data -> create sample movies for statistics
        sample_movies = [
            Movie("Movie 1", 2020, "Description 1", rating=8.0, tags=["action"]),
            Movie("Movie 2", 2021, "Description 2", rating=7.5, tags=["drama"]),
        ]

        # adapter.web.mock.repository -> configure repository mock
        mock_repository = Mock(spec=MovieRepository)
        mock_repository.find_all.return_value = sample_movies
        mock_repository.count.return_value = len(sample_movies)

        # adapter.web.test.setup -> create test client
        app = create_app(mock_repository)
        client = app.test_client()

        # adapter.web.request.get_stats -> execute GET statistics request
        response = client.get('/statistics')

        # adapter.web.verification.statistics_response -> correct statistics returned
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['total_movies'] == 2
        assert data['average_rating'] == 7.75
        assert data['movies_with_ratings'] == 2
        assert 'unique_tags' in data

    def test_web_adapter_integration_with_real_repository(self):
        """
        Test web adapter with real in-memory repository (integration test).

        Adapter.Web.Integration -> full stack integration test
        """
        from movie_web_adapter import create_app

        # adapter.web.integration.real_repository -> use actual repository
        repository = InMemoryMovieRepository()

        # adapter.web.integration.setup -> create app with real repository
        app = create_app(repository)
        client = app.test_client()

        # adapter.web.integration.workflow -> complete CRUD workflow

        # 1. Add a movie
        movie_data = {
            "title": "Integration Test Movie",
            "year": 2023,
            "description": "Testing integration",
            "rating": 8.0,
            "tags": ["test"]
        }

        post_response = client.post('/movies',
                                   data=json.dumps(movie_data),
                                   content_type='application/json')
        assert post_response.status_code == 201
        created_movie = json.loads(post_response.data)
        movie_id = created_movie['id']

        # 2. Retrieve the movie
        get_response = client.get(f'/movies/{movie_id}')
        assert get_response.status_code == 200
        retrieved_movie = json.loads(get_response.data)
        assert retrieved_movie['title'] == "Integration Test Movie"

        # 3. List all movies
        list_response = client.get('/movies')
        assert list_response.status_code == 200
        all_movies = json.loads(list_response.data)
        assert len(all_movies) == 1

        # 4. Update rating
        rating_update = {"rating": 9.5}
        put_response = client.put(f'/movies/{movie_id}/rating',
                                 data=json.dumps(rating_update),
                                 content_type='application/json')
        assert put_response.status_code == 200

        # 5. Verify rating update
        updated_response = client.get(f'/movies/{movie_id}')
        updated_movie = json.loads(updated_response.data)
        assert updated_movie['rating'] == 9.5

        # 6. Delete the movie
        delete_response = client.delete(f'/movies/{movie_id}')
        assert delete_response.status_code == 204

        # 7. Verify deletion
        final_list_response = client.get('/movies')
        final_movies = json.loads(final_list_response.data)
        assert len(final_movies) == 0