"""
Test suite for in-memory movie repository adapter.

This module tests the concrete in-memory implementation of the MovieRepository
port interface. This adapter serves as both a mock for TDD and a lightweight
storage solution for development/testing scenarios.
"""

import pytest
from typing import List
from movie_domain import Movie
from movie_repository import MovieRepository


class TestInMemoryMovieRepository:
    """Test cases for the InMemoryMovieRepository adapter."""

    def test_repository_implements_interface(self):
        """
        Test that InMemoryMovieRepository properly implements MovieRepository.

        Adapter.InMemory.Interface_Compliance -> concrete implementation of port
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.repository.implementation -> concrete class implements interface
        repository = InMemoryMovieRepository()

        # adapter.interface.compliance -> instance implements all required methods
        assert isinstance(repository, MovieRepository)

        # adapter.method.availability -> all port methods are callable
        assert callable(getattr(repository, 'save'))
        assert callable(getattr(repository, 'find_by_id'))
        assert callable(getattr(repository, 'find_all'))
        assert callable(getattr(repository, 'find_by_filters'))
        assert callable(getattr(repository, 'delete'))
        assert callable(getattr(repository, 'count'))

    def test_repository_starts_empty(self):
        """
        Test that new repository instance starts with no movies.

        Adapter.InMemory.Initial_State -> empty storage on instantiation
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.initial_state -> new repository contains no movies
        repository = InMemoryMovieRepository()

        # adapter.storage.empty_verification -> count and find_all confirm empty state
        assert repository.count() == 0
        assert repository.find_all() == []

    def test_repository_save_and_retrieve_movie(self):
        """
        Test basic save and retrieval operations.

        Adapter.InMemory.Basic_CRUD -> fundamental storage operations
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.movie_creation -> create test movie entity
        movie = Movie("Test Movie", 2023, "A test movie description")

        # adapter.repository.instance -> create storage adapter
        repository = InMemoryMovieRepository()

        # adapter.operation.save -> persist movie to storage
        repository.save(movie)

        # adapter.storage.persistence_verification -> movie stored successfully
        assert repository.count() == 1

        # adapter.operation.retrieval.by_id -> find movie by identifier
        retrieved_movie = repository.find_by_id(movie.id)

        # adapter.storage.retrieval_verification -> retrieved movie matches saved
        assert retrieved_movie is not None
        assert retrieved_movie.id == movie.id
        assert retrieved_movie.title == "Test Movie"
        assert retrieved_movie.year == 2023

    def test_repository_save_multiple_movies(self):
        """
        Test saving and managing multiple movies.

        Adapter.InMemory.Multiple_Entities -> collection storage operations
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.multiple_movies -> create several test movies
        movie1 = Movie("First Movie", 2021, "First description")
        movie2 = Movie("Second Movie", 2022, "Second description")
        movie3 = Movie("Third Movie", 2023, "Third description")

        # adapter.repository.instance -> create storage adapter
        repository = InMemoryMovieRepository()

        # adapter.operation.multiple_saves -> store all movies
        repository.save(movie1)
        repository.save(movie2)
        repository.save(movie3)

        # adapter.storage.multiple_verification -> all movies stored
        assert repository.count() == 3

        # adapter.operation.find_all -> retrieve complete collection
        all_movies = repository.find_all()

        # adapter.storage.collection_verification -> all movies retrievable
        assert len(all_movies) == 3
        # adapter.storage.identity_preservation -> each movie maintains unique identity
        movie_ids = {movie.id for movie in all_movies}
        assert len(movie_ids) == 3  # All IDs are unique

    def test_repository_update_existing_movie(self):
        """
        Test updating an existing movie (save overwrites).

        Adapter.InMemory.Update_Operation -> modify existing entity
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.movie_creation -> create test movie
        movie = Movie("Original Title", 2020, "Original description")

        # adapter.repository.instance -> create storage adapter
        repository = InMemoryMovieRepository()
        repository.save(movie)

        # adapter.storage.initial_verification -> movie saved successfully
        assert repository.count() == 1
        original_id = movie.id

        # adapter.operation.movie_modification -> modify movie entity
        movie.rate(8.5)
        movie.add_tag("drama")

        # adapter.operation.update_save -> save modified movie
        repository.save(movie)

        # adapter.storage.update_verification -> count remains same (update, not insert)
        assert repository.count() == 1

        # adapter.operation.retrieval.updated -> retrieve updated movie
        updated_movie = repository.find_by_id(original_id)

        # adapter.storage.modification_verification -> changes persisted
        assert updated_movie.rating == 8.5
        assert "drama" in updated_movie.tags

    def test_repository_delete_movie(self):
        """
        Test deleting a movie from storage.

        Adapter.InMemory.Delete_Operation -> remove entity from storage
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.movie_creation -> create test movie
        movie = Movie("To Be Deleted", 2023, "This movie will be removed")

        # adapter.repository.instance -> create storage adapter
        repository = InMemoryMovieRepository()
        repository.save(movie)

        # adapter.storage.pre_delete_verification -> movie exists before deletion
        assert repository.count() == 1
        assert repository.find_by_id(movie.id) is not None

        # adapter.operation.delete -> remove movie by ID
        delete_result = repository.delete(movie.id)

        # adapter.storage.delete_verification -> movie successfully removed
        assert delete_result is True
        assert repository.count() == 0
        assert repository.find_by_id(movie.id) is None

    def test_repository_delete_nonexistent_movie(self):
        """
        Test deleting a movie that doesn't exist.

        Adapter.InMemory.Delete_Missing -> safe handling of nonexistent entities
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.repository.instance -> create empty storage adapter
        repository = InMemoryMovieRepository()

        # adapter.operation.delete_missing -> attempt to delete nonexistent movie
        delete_result = repository.delete("nonexistent-id")

        # adapter.storage.delete_missing_verification -> operation reports failure safely
        assert delete_result is False
        assert repository.count() == 0

    def test_repository_find_by_title_filter(self):
        """
        Test filtering movies by title substring.

        Adapter.InMemory.Filter_Title -> text-based search functionality
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.test_data -> create movies with different titles
        movie1 = Movie("The Matrix", 1999, "Sci-fi classic")
        movie2 = Movie("Matrix Reloaded", 2003, "Sequel")
        movie3 = Movie("Inception", 2010, "Dreams within dreams")

        # adapter.repository.setup -> store test movies
        repository = InMemoryMovieRepository()
        repository.save(movie1)
        repository.save(movie2)
        repository.save(movie3)

        # adapter.operation.filter.title -> search by partial title
        matrix_movies = repository.find_by_filters(title="Matrix")

        # adapter.filter.title_verification -> correct movies returned
        assert len(matrix_movies) == 2
        # adapter.filter.title_content -> both Matrix movies found
        titles = {movie.title for movie in matrix_movies}
        assert "The Matrix" in titles
        assert "Matrix Reloaded" in titles
        assert "Inception" not in titles

    def test_repository_find_by_year_filter(self):
        """
        Test filtering movies by exact year.

        Adapter.InMemory.Filter_Year -> temporal filtering functionality
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.test_data -> create movies from different years
        movie1 = Movie("Movie 2020", 2020, "From 2020")
        movie2 = Movie("Movie 2021", 2021, "From 2021")
        movie3 = Movie("Another 2021", 2021, "Also from 2021")

        # adapter.repository.setup -> store test movies
        repository = InMemoryMovieRepository()
        repository.save(movie1)
        repository.save(movie2)
        repository.save(movie3)

        # adapter.operation.filter.year -> search by specific year
        movies_2021 = repository.find_by_filters(year=2021)

        # adapter.filter.year_verification -> correct movies returned
        assert len(movies_2021) == 2
        # adapter.filter.year_content -> both 2021 movies found
        for movie in movies_2021:
            assert movie.year == 2021

    def test_repository_find_by_rating_range_filter(self):
        """
        Test filtering movies by rating range.

        Adapter.InMemory.Filter_Rating -> numeric range filtering functionality
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.test_data -> create movies with different ratings
        movie1 = Movie("Low Rated", 2020, "Not great", rating=3.5)
        movie2 = Movie("Medium Rated", 2021, "Pretty good", rating=7.0)
        movie3 = Movie("High Rated", 2022, "Excellent", rating=9.5)
        movie4 = Movie("Unrated", 2023, "No rating yet")  # No rating

        # adapter.repository.setup -> store test movies
        repository = InMemoryMovieRepository()
        repository.save(movie1)
        repository.save(movie2)
        repository.save(movie3)
        repository.save(movie4)

        # adapter.operation.filter.rating_range -> search by rating bounds
        good_movies = repository.find_by_filters(rating_min=7.0, rating_max=10.0)

        # adapter.filter.rating_verification -> correct movies returned
        assert len(good_movies) == 2
        # adapter.filter.rating_content -> high-rated movies found
        titles = {movie.title for movie in good_movies}
        assert "Medium Rated" in titles
        assert "High Rated" in titles
        assert "Low Rated" not in titles
        assert "Unrated" not in titles

    def test_repository_find_by_tags_filter(self):
        """
        Test filtering movies by required tags.

        Adapter.InMemory.Filter_Tags -> category-based filtering functionality
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.test_data -> create movies with different tag combinations
        movie1 = Movie("Sci-Fi Drama", 2020, "Space drama", tags=["sci-fi", "drama"])
        movie2 = Movie("Action Sci-Fi", 2021, "Space action", tags=["sci-fi", "action"])
        movie3 = Movie("Pure Drama", 2022, "Character study", tags=["drama"])
        movie4 = Movie("No Tags", 2023, "Untagged movie")  # No tags

        # adapter.repository.setup -> store test movies
        repository = InMemoryMovieRepository()
        repository.save(movie1)
        repository.save(movie2)
        repository.save(movie3)
        repository.save(movie4)

        # adapter.operation.filter.tags -> search by required tags
        scifi_movies = repository.find_by_filters(tags=["sci-fi"])

        # adapter.filter.tags_verification -> movies with sci-fi tag returned
        assert len(scifi_movies) == 2
        # adapter.filter.tags_content -> sci-fi movies found
        titles = {movie.title for movie in scifi_movies}
        assert "Sci-Fi Drama" in titles
        assert "Action Sci-Fi" in titles

    def test_repository_find_by_multiple_filters(self):
        """
        Test combining multiple filter criteria.

        Adapter.InMemory.Filter_Combined -> multi-criteria filtering functionality
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.test_data -> create diverse movie collection
        movie1 = Movie("Great Sci-Fi", 2020, "Amazing space opera", rating=9.0, tags=["sci-fi"])
        movie2 = Movie("Good Sci-Fi", 2020, "Decent space story", rating=7.5, tags=["sci-fi"])
        movie3 = Movie("Great Drama", 2020, "Amazing character study", rating=9.2, tags=["drama"])
        movie4 = Movie("Old Sci-Fi", 1980, "Classic space tale", rating=8.5, tags=["sci-fi"])

        # adapter.repository.setup -> store test movies
        repository = InMemoryMovieRepository()
        repository.save(movie1)
        repository.save(movie2)
        repository.save(movie3)
        repository.save(movie4)

        # adapter.operation.filter.combined -> search with multiple criteria
        filtered_movies = repository.find_by_filters(
            year=2020,
            rating_min=8.0,
            tags=["sci-fi"]
        )

        # adapter.filter.combined_verification -> only movie matching all criteria
        assert len(filtered_movies) == 1
        # adapter.filter.combined_content -> correct movie found
        assert filtered_movies[0].title == "Great Sci-Fi"

    def test_repository_find_with_no_matches(self):
        """
        Test filtering that returns no results.

        Adapter.InMemory.Filter_No_Matches -> empty result handling
        """
        from in_memory_repository import InMemoryMovieRepository

        # adapter.storage.test_data -> create limited movie collection
        movie = Movie("Only Movie", 2020, "The single movie", tags=["drama"])

        # adapter.repository.setup -> store single test movie
        repository = InMemoryMovieRepository()
        repository.save(movie)

        # adapter.operation.filter.no_matches -> search with no matching criteria
        no_matches = repository.find_by_filters(tags=["sci-fi"])

        # adapter.filter.no_matches_verification -> empty list returned
        assert len(no_matches) == 0
        assert no_matches == []