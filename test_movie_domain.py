"""
Test suite for movie catalog domain entities.

This module tests the core domain logic for the hexagonal architecture's center.
Following TDD principles - tests written first to define behavior.
"""

import pytest
from datetime import datetime
from typing import List, Optional

# Test will drive the creation of our domain entities


class TestMovieEntity:
    """Test cases for the Movie domain entity."""

    def test_movie_creation_with_required_fields(self):
        """
        Test that a Movie can be created with minimum required fields.

        Domain.Movie.creation.required_fields -> title, year, description
        """
        # domain.movie.entity.title -> string identifier for the film
        # domain.movie.entity.year -> integer release year
        # domain.movie.entity.description -> string plot/synopsis
        from movie_domain import Movie

        movie = Movie(
            title="The Matrix",
            year=1999,
            description="A computer programmer discovers reality is a simulation"
        )

        assert movie.title == "The Matrix"
        assert movie.year == 1999
        assert movie.description == "A computer programmer discovers reality is a simulation"
        # domain.movie.entity.rating -> optional numeric score (initially None)
        assert movie.rating is None
        # domain.movie.entity.tags -> optional list of categorization strings
        assert movie.tags == []
        # domain.movie.entity.id -> unique identifier (auto-generated)
        assert movie.id is not None

    def test_movie_creation_with_all_fields(self):
        """
        Test Movie creation with all optional fields populated.

        Domain.Movie.creation.complete_fields -> all entity attributes
        """
        from movie_domain import Movie

        # domain.movie.entity.tags.list -> collection of string categorizations
        tags_collection = ["sci-fi", "action", "philosophy"]
        # domain.movie.entity.rating.score -> numeric rating between 1-10
        rating_score = 9.5

        movie = Movie(
            title="Blade Runner 2049",
            year=2017,
            description="A young blade runner discovers a secret that could plunge society into chaos",
            rating=rating_score,
            tags=tags_collection
        )

        assert movie.rating == 9.5
        assert movie.tags == ["sci-fi", "action", "philosophy"]

    def test_movie_rating_validation(self):
        """
        Test that movie rating must be within valid range.

        Domain.Movie.validation.rating_bounds -> 1.0 to 10.0 inclusive
        """
        from movie_domain import Movie, InvalidRatingError

        # domain.validation.rating.minimum -> below 1.0 should raise error
        with pytest.raises(InvalidRatingError):
            Movie("Test", 2000, "Test description", rating=0.5)

        # domain.validation.rating.maximum -> above 10.0 should raise error
        with pytest.raises(InvalidRatingError):
            Movie("Test", 2000, "Test description", rating=10.5)

        # domain.validation.rating.valid_bounds -> 1.0 and 10.0 should work
        movie_min = Movie("Test Min", 2000, "Test", rating=1.0)
        movie_max = Movie("Test Max", 2000, "Test", rating=10.0)

        assert movie_min.rating == 1.0
        assert movie_max.rating == 10.0

    def test_movie_year_validation(self):
        """
        Test that movie year must be reasonable.

        Domain.Movie.validation.year_bounds -> realistic film production years
        """
        from movie_domain import Movie, InvalidYearError

        # domain.validation.year.minimum -> films before 1888 (first motion picture)
        with pytest.raises(InvalidYearError):
            Movie("Impossible Film", 1800, "Too early")

        # domain.validation.year.maximum -> films in far future are unrealistic
        current_year = datetime.now().year  # domain.time.current.year
        future_limit = current_year + 10    # domain.validation.year.future_buffer

        with pytest.raises(InvalidYearError):
            Movie("Far Future Film", future_limit + 1, "Too far ahead")

    def test_movie_title_validation(self):
        """
        Test that movie title cannot be empty or just whitespace.

        Domain.Movie.validation.title_content -> non-empty meaningful string
        """
        from movie_domain import Movie, InvalidTitleError

        # domain.validation.title.empty -> empty string should raise error
        with pytest.raises(InvalidTitleError):
            Movie("", 2000, "Test description")

        # domain.validation.title.whitespace -> only spaces should raise error
        with pytest.raises(InvalidTitleError):
            Movie("   ", 2000, "Test description")

    def test_movie_id_uniqueness(self):
        """
        Test that each movie gets a unique identifier.

        Domain.Movie.identity.uniqueness -> no two movies share same ID
        """
        from movie_domain import Movie

        # domain.movie.entity.id.generation -> auto-generated unique identifier
        movie1 = Movie("Movie One", 2000, "First movie")
        movie2 = Movie("Movie Two", 2001, "Second movie")

        # domain.identity.uniqueness.constraint -> IDs must differ
        assert movie1.id != movie2.id
        assert movie1.id is not None
        assert movie2.id is not None

    def test_movie_update_rating(self):
        """
        Test that movie rating can be updated after creation.

        Domain.Movie.mutation.rating_update -> modify rating on existing entity
        """
        from movie_domain import Movie

        # domain.movie.entity.initial_state -> rating starts as None
        movie = Movie("Updatable Movie", 2020, "Can be rated later")
        assert movie.rating is None

        # domain.movie.behavior.rate -> method to set/update rating
        movie.rate(8.5)
        # domain.movie.state.rating_updated -> rating now reflects new value
        assert movie.rating == 8.5

        # domain.movie.behavior.re_rate -> rating can be changed again
        movie.rate(9.0)
        assert movie.rating == 9.0

    def test_movie_add_tags(self):
        """
        Test that tags can be added to a movie after creation.

        Domain.Movie.mutation.tags_management -> add/remove categorization
        """
        from movie_domain import Movie

        # domain.movie.entity.tags.initial -> starts as empty list
        movie = Movie("Taggable Movie", 2021, "Can be categorized")
        assert movie.tags == []

        # domain.movie.behavior.add_tag -> method to append single tag
        movie.add_tag("thriller")
        # domain.movie.state.tags_updated -> tags list now contains new tag
        assert "thriller" in movie.tags
        assert len(movie.tags) == 1

        # domain.movie.behavior.add_multiple_tags -> can add more tags
        movie.add_tag("mystery")
        movie.add_tag("drama")
        # domain.movie.state.tags_collection -> all tags preserved in list
        assert set(movie.tags) == {"thriller", "mystery", "drama"}

    def test_movie_remove_tags(self):
        """
        Test that tags can be removed from a movie.

        Domain.Movie.mutation.tags_removal -> remove specific categorization
        """
        from movie_domain import Movie

        # domain.movie.entity.tags.populated -> start with existing tags
        movie = Movie("Tagged Movie", 2022, "Has tags", tags=["action", "comedy", "romance"])

        # domain.movie.behavior.remove_tag -> method to remove specific tag
        movie.remove_tag("comedy")
        # domain.movie.state.tags_after_removal -> tag no longer in collection
        assert "comedy" not in movie.tags
        assert set(movie.tags) == {"action", "romance"}

        # domain.movie.behavior.remove_nonexistent_tag -> removing missing tag is safe
        movie.remove_tag("horror")  # domain.operation.safe_removal -> no error
        assert set(movie.tags) == {"action", "romance"}