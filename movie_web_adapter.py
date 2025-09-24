"""
Flask web adapter for the movie catalog application.

This module provides the Flask web adapter that serves as a primary adapter
in our hexagonal architecture. It exposes REST API endpoints for movie
catalog operations, demonstrating how the same application services can
be driven by different interfaces (CLI vs Web API).

Web adapter responsibilities:
- Expose REST API endpoints for movie operations
- Handle HTTP request/response formatting
- Coordinate application services (command and query)
- Provide error handling and status codes
- Serve as alternative to CLI adapter
"""

from flask import Flask, request, jsonify
from typing import Dict, Any, List, Optional
from movie_domain import Movie, InvalidRatingError, InvalidTitleError, InvalidYearError
from movie_repository import MovieRepository, InvalidFilterError
from movie_command_service import MovieCommandService
from movie_query_service import MovieQueryService
from in_memory_repository import InMemoryMovieRepository


def create_app(repository: MovieRepository) -> Flask:
    """
    Create and configure Flask application with repository dependency.

    Args:
        repository: MovieRepository implementation for data persistence

    Returns:
        Configured Flask application instance

    Adapter.Web.Factory -> application factory pattern with dependency injection
    """
    # adapter.web.flask.creation -> create Flask application instance
    app = Flask(__name__)

    # adapter.web.services.application_layer -> create coordinated application services
    command_service = MovieCommandService(repository)
    query_service = MovieQueryService(repository)

    # adapter.web.routes.movies -> movie CRUD endpoints
    @app.route('/movies', methods=['GET'])
    def get_movies():
        """
        Get all movies or filter movies based on query parameters.

        Query Parameters:
        - title: Filter by title substring
        - year: Filter by exact year
        - min_rating: Minimum rating filter
        - max_rating: Maximum rating filter
        - tags: Comma-separated list of required tags

        Returns:
            JSON array of movie objects

        Adapter.Web.Endpoint.Get_Movies -> retrieve movie collection with optional filtering
        """
        try:
            # adapter.web.request.query_params -> extract filtering parameters
            title = request.args.get('title')
            year_str = request.args.get('year')
            min_rating_str = request.args.get('min_rating')
            max_rating_str = request.args.get('max_rating')
            tags_str = request.args.get('tags')

            # adapter.web.parsing.parameters -> convert string parameters to appropriate types
            year = int(year_str) if year_str else None
            min_rating = float(min_rating_str) if min_rating_str else None
            max_rating = float(max_rating_str) if max_rating_str else None
            tags = tags_str.split(',') if tags_str else None

            # adapter.web.service.query -> execute search through query service
            if not any([title, year, min_rating, max_rating, tags]):
                # No filters specified, get all movies
                movies = query_service.get_all_movies()
            else:
                # Filters specified, use search
                movies = query_service.search_movies(
                    title=title,
                    year=year,
                    rating_min=min_rating,
                    rating_max=max_rating,
                    tags=tags
                )

            # adapter.web.serialization.movies -> convert movies to JSON-serializable format
            return jsonify([_movie_to_dict(movie) for movie in movies])

        except (ValueError, InvalidFilterError) as e:
            # adapter.web.error.bad_request -> handle parameter validation errors
            return jsonify({'error': str(e)}), 400

        except Exception as e:
            # adapter.web.error.internal -> handle unexpected errors
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    @app.route('/movies', methods=['POST'])
    def create_movie():
        """
        Create a new movie in the catalog.

        Request Body (JSON):
        - title: Movie title (required)
        - year: Release year (required)
        - description: Movie description (required)
        - rating: Movie rating 1.0-10.0 (optional)
        - tags: Array of tag strings (optional)

        Returns:
            JSON object of created movie with 201 status

        Adapter.Web.Endpoint.Post_Movie -> create new movie via API
        """
        try:
            # adapter.web.request.json_body -> extract JSON payload
            data = request.get_json()

            if not data:
                return jsonify({'error': 'JSON payload required'}), 400

            # adapter.web.validation.required_fields -> check required parameters
            required_fields = ['title', 'year', 'description']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # adapter.web.service.command -> create movie through command service
            movie = command_service.add_movie(
                title=data['title'],
                year=data['year'],
                description=data['description'],
                rating=data.get('rating'),
                tags=data.get('tags')
            )

            # adapter.web.response.created -> return created movie with 201 status
            return jsonify(_movie_to_dict(movie)), 201

        except (InvalidTitleError, InvalidYearError, InvalidRatingError) as e:
            # adapter.web.error.domain_validation -> handle domain validation errors
            return jsonify({'error': str(e)}), 400

        except Exception as e:
            # adapter.web.error.internal -> handle unexpected errors
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    @app.route('/movies/<movie_id>', methods=['GET'])
    def get_movie_by_id(movie_id: str):
        """
        Get a specific movie by its ID.

        Args:
            movie_id: Unique identifier for the movie

        Returns:
            JSON object of movie or 404 if not found

        Adapter.Web.Endpoint.Get_Movie_By_Id -> retrieve single movie by identifier
        """
        try:
            # adapter.web.service.query -> find movie through query service
            movie = query_service.get_movie_by_id(movie_id)

            if movie is None:
                # adapter.web.response.not_found -> return 404 for missing movie
                return jsonify({'error': f'Movie with ID {movie_id} not found'}), 404

            # adapter.web.response.movie -> return movie data
            return jsonify(_movie_to_dict(movie))

        except Exception as e:
            # adapter.web.error.internal -> handle unexpected errors
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    @app.route('/movies/<movie_id>/rating', methods=['PUT'])
    def update_movie_rating(movie_id: str):
        """
        Update the rating of a specific movie.

        Args:
            movie_id: Unique identifier for the movie

        Request Body (JSON):
        - rating: New rating value (1.0-10.0)

        Returns:
            Success message or error

        Adapter.Web.Endpoint.Put_Rating -> update movie rating via API
        """
        try:
            # adapter.web.request.json_body -> extract rating update payload
            data = request.get_json()

            if not data or 'rating' not in data:
                return jsonify({'error': 'Rating value required'}), 400

            # adapter.web.service.command -> update rating through command service
            success = command_service.rate_movie(movie_id, data['rating'])

            if not success:
                # adapter.web.response.not_found -> movie not found for rating update
                return jsonify({'error': f'Movie with ID {movie_id} not found'}), 404

            # adapter.web.response.success -> confirm successful rating update
            return jsonify({'message': f'Rating updated to {data["rating"]}'})

        except InvalidRatingError as e:
            # adapter.web.error.domain_validation -> handle rating validation error
            return jsonify({'error': str(e)}), 400

        except Exception as e:
            # adapter.web.error.internal -> handle unexpected errors
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    @app.route('/movies/<movie_id>/tags', methods=['POST'])
    def add_movie_tag(movie_id: str):
        """
        Add a tag to a specific movie.

        Args:
            movie_id: Unique identifier for the movie

        Request Body (JSON):
        - tag: Tag string to add

        Returns:
            Success message or error

        Adapter.Web.Endpoint.Post_Tag -> add tag to movie via API
        """
        try:
            # adapter.web.request.json_body -> extract tag payload
            data = request.get_json()

            if not data or 'tag' not in data:
                return jsonify({'error': 'Tag value required'}), 400

            # adapter.web.service.command -> add tag through command service
            success = command_service.add_tag_to_movie(movie_id, data['tag'])

            if not success:
                # adapter.web.response.not_found -> movie not found for tag addition
                return jsonify({'error': f'Movie with ID {movie_id} not found'}), 404

            # adapter.web.response.success -> confirm successful tag addition
            return jsonify({'message': f'Tag "{data["tag"]}" added'})

        except Exception as e:
            # adapter.web.error.internal -> handle unexpected errors
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    @app.route('/movies/<movie_id>/tags/<tag>', methods=['DELETE'])
    def remove_movie_tag(movie_id: str, tag: str):
        """
        Remove a tag from a specific movie.

        Args:
            movie_id: Unique identifier for the movie
            tag: Tag string to remove

        Returns:
            Success message or error

        Adapter.Web.Endpoint.Delete_Tag -> remove tag from movie via API
        """
        try:
            # adapter.web.service.command -> remove tag through command service
            success = command_service.remove_tag_from_movie(movie_id, tag)

            if not success:
                # adapter.web.response.not_found -> movie not found for tag removal
                return jsonify({'error': f'Movie with ID {movie_id} not found'}), 404

            # adapter.web.response.success -> confirm successful tag removal
            return jsonify({'message': f'Tag "{tag}" removed'})

        except Exception as e:
            # adapter.web.error.internal -> handle unexpected errors
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    @app.route('/movies/<movie_id>', methods=['DELETE'])
    def delete_movie(movie_id: str):
        """
        Delete a specific movie from the catalog.

        Args:
            movie_id: Unique identifier for the movie

        Returns:
            204 No Content on success, 404 if not found

        Adapter.Web.Endpoint.Delete_Movie -> remove movie via API
        """
        try:
            # adapter.web.service.command -> delete movie through command service
            success = command_service.delete_movie(movie_id)

            if not success:
                # adapter.web.response.not_found -> movie not found for deletion
                return jsonify({'error': f'Movie with ID {movie_id} not found'}), 404

            # adapter.web.response.no_content -> successful deletion with no content
            return '', 204

        except Exception as e:
            # adapter.web.error.internal -> handle unexpected errors
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    @app.route('/statistics', methods=['GET'])
    def get_catalog_statistics():
        """
        Get comprehensive statistics about the movie catalog.

        Returns:
            JSON object with catalog statistics

        Adapter.Web.Endpoint.Get_Statistics -> catalog analytics via API
        """
        try:
            # adapter.web.service.query -> get statistics through query service
            stats = query_service.get_catalog_statistics()

            # adapter.web.serialization.statistics -> convert statistics to JSON-safe format
            serialized_stats = {
                'total_movies': stats['total_movies'],
                'movies_with_ratings': stats['movies_with_ratings'],
                'average_rating': stats['average_rating'],
                'unique_tags': list(stats['unique_tags']),  # Convert set to list for JSON
                'year_range': stats['year_range']
            }

            # adapter.web.response.statistics -> return statistics data
            return jsonify(serialized_stats)

        except Exception as e:
            # adapter.web.error.internal -> handle unexpected errors
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    @app.route('/', methods=['GET'])
    def index():
        """
        Display API documentation with all available routes.

        Returns:
            HTML page with comprehensive API documentation and examples

        Adapter.Web.Endpoint.Index -> API documentation and route discovery
        """
        # adapter.web.documentation -> comprehensive API route listing
        routes_info = [
            {
                "route": "GET /",
                "description": "API documentation and route listing",
                "parameters": "None",
                "example_url": "/"
            },
            {
                "route": "GET /movies",
                "description": "Retrieve all movies with optional filtering",
                "parameters": "title (string), year (int), min_rating (float), max_rating (float), tags (comma-separated)",
                "example_url": "/movies?tags=sci-fi&min_rating=8.0"
            },
            {
                "route": "POST /movies",
                "description": "Create a new movie entry",
                "parameters": "JSON body: title (required), year (required), description (required), rating (optional), tags (optional array)",
                "example_url": "/movies"
            },
            {
                "route": "GET /movies/{id}",
                "description": "Retrieve a specific movie by its unique ID",
                "parameters": "id (string) - Movie's unique identifier",
                "example_url": "/movies/sample-movie-id"
            },
            {
                "route": "PUT /movies/{id}/rating",
                "description": "Update a movie's rating",
                "parameters": "id (string), JSON body: rating (float 1.0-10.0)",
                "example_url": "/movies/sample-movie-id/rating"
            },
            {
                "route": "POST /movies/{id}/tags",
                "description": "Add a tag to a movie",
                "parameters": "id (string), JSON body: tag (string)",
                "example_url": "/movies/sample-movie-id/tags"
            },
            {
                "route": "DELETE /movies/{id}/tags/{tag}",
                "description": "Remove a specific tag from a movie",
                "parameters": "id (string), tag (string)",
                "example_url": "/movies/sample-movie-id/tags/sci-fi"
            },
            {
                "route": "DELETE /movies/{id}",
                "description": "Delete a movie from the catalog",
                "parameters": "id (string) - Movie's unique identifier",
                "example_url": "/movies/sample-movie-id"
            },
            {
                "route": "GET /statistics",
                "description": "Get comprehensive catalog statistics and analytics",
                "parameters": "None",
                "example_url": "/statistics"
            }
        ]

        # adapter.web.html_generation -> create interactive documentation
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Catalog API - Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background: #f8f9fa;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .route-card {
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .route-method {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
            margin-right: 10px;
        }
        .route-path {
            font-family: 'Monaco', 'Menlo', monospace;
            font-weight: bold;
            font-size: 1.1em;
        }
        .description {
            color: #666;
            margin: 10px 0;
        }
        .parameters {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 0.9em;
        }
        .example-link {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 10px;
            font-weight: 500;
        }
        .example-link:hover {
            background: #218838;
            text-decoration: none;
            color: white;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            color: #666;
        }
        .architecture-badge {
            display: inline-block;
            background: #fd7e14;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 Movie Catalog API</h1>
        <p>Hexagonal Architecture • REST API • Personal Movie Collection Manager</p>
        <div>
            <span class="architecture-badge">Domain-Driven Design</span>
            <span class="architecture-badge">CQRS</span>
            <span class="architecture-badge">Ports & Adapters</span>
            <span class="architecture-badge">Test-Driven</span>
        </div>
    </div>

    <h2>🚀 Available API Endpoints</h2>
    <p>Click the green "Try It" links to test each endpoint with sample data.</p>
"""

        # adapter.web.route_documentation -> generate route cards
        for route_info in routes_info:
            method = route_info['route'].split()[0]
            path = route_info['route'].split(' ', 1)[1]

            # adapter.web.method_color -> visual method identification
            method_color = {
                'GET': '#28a745',
                'POST': '#007bff',
                'PUT': '#ffc107',
                'DELETE': '#dc3545'
            }.get(method, '#6c757d')

            html_content += f"""
    <div class="route-card">
        <div>
            <span class="route-method" style="background-color: {method_color}">{method}</span>
            <span class="route-path">{path}</span>
        </div>
        <div class="description">{route_info['description']}</div>
        <div class="parameters"><strong>Parameters:</strong> {route_info['parameters']}</div>
        <a href="{route_info['example_url']}" class="example-link">Try It →</a>
    </div>
"""

        html_content += """
    <div class="footer">
        <h3>🏗️ Architecture Highlights</h3>
        <p>This API demonstrates <strong>Hexagonal Architecture</strong> principles:</p>
        <ul style="text-align: left; display: inline-block;">
            <li><strong>Domain Layer:</strong> Rich Movie entity with business rules</li>
            <li><strong>Application Services:</strong> Command/Query separation (CQRS)</li>
            <li><strong>Port Interfaces:</strong> Repository abstraction for storage</li>
            <li><strong>Adapters:</strong> This Web API + CLI interface</li>
            <li><strong>Dependency Inversion:</strong> Core depends on abstractions</li>
        </ul>
        <p><em>Same business logic accessible via CLI and Web API • 72 comprehensive tests</em></p>
    </div>
</body>
</html>
"""

        # adapter.web.response.documentation -> return interactive HTML documentation
        return html_content

    # adapter.web.error_handlers -> global error handling
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors with JSON response."""
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Handle 405 method not allowed errors."""
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 internal server errors."""
        return jsonify({'error': 'Internal server error'}), 500

    return app


def _movie_to_dict(movie: Movie) -> Dict[str, Any]:
    """
    Convert a Movie entity to a JSON-serializable dictionary.

    Args:
        movie: Movie entity to serialize

    Returns:
        Dictionary representation of the movie

    Adapter.Web.Serialization.Movie -> convert domain entity to web format
    """
    # adapter.web.serialization.entity_to_dict -> map domain entity to dictionary
    return {
        'id': movie.id,
        'title': movie.title,
        'year': movie.year,
        'description': movie.description,
        'rating': movie.rating,
        'tags': movie.tags
    }


def main():
    """
    Main entry point for running the Flask web application.

    Adapter.Web.Main -> standalone web server entry point
    """
    # adapter.web.main.repository -> create in-memory repository for web usage
    repository = InMemoryMovieRepository()

    # adapter.web.main.app -> create Flask application
    app = create_app(repository)

    # adapter.web.main.run -> start development server
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == "__main__":
    main()