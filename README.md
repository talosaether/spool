# Movie Catalog

> A personal movie collection manager demonstrating **Hexagonal Architecture** and **Shape Up** methodology.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and start the web API
git clone <repository-url>
cd movie-catalog
docker-compose up

# Web API available at http://localhost:5000
curl http://localhost:5000/movies
```

### Option 2: Local Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Run tests (72 tests)
pytest -v

# Start web API
python movie_web_adapter.py

# Or use CLI
python movie_cli.py --help
```

## 📖 Usage

### Web API (REST)

```bash
# Add a movie
curl -X POST http://localhost:5000/movies \
  -H "Content-Type: application/json" \
  -d '{"title": "The Matrix", "year": 1999, "description": "Sci-fi classic", "rating": 9.0, "tags": ["sci-fi", "action"]}'

# Get all movies
curl http://localhost:5000/movies

# Filter movies
curl "http://localhost:5000/movies?tags=sci-fi&min_rating=8.0"

# Get statistics
curl http://localhost:5000/statistics
```

### CLI

```bash
# Add a movie
python movie_cli.py add "Inception" 2010 "Dreams within dreams" --rating 8.8 --tags sci-fi thriller

# List movies
python movie_cli.py list --tags sci-fi

# Search by title
python movie_cli.py search "Matrix"

# Interactive test environment
python movie_cli.py test
```

## 🧪 Testing

```bash
# Run all tests (72 tests across all layers)
pytest -v

# Test specific layer
pytest test_movie_domain.py -v      # Domain layer
pytest test_movie_web_adapter.py -v # Web API
```

## 🏗️ Architecture

This project demonstrates **Hexagonal Architecture** (Ports & Adapters) with clean separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐
│   CLI Adapter   │    │  Web Adapter    │
│  (Primary)      │    │  (Primary)      │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
    ┌────────────────▼────────────────┐
    │        Application Layer        │
    │  ┌─────────────┐ ┌─────────────┐│
    │  │   Command   │ │    Query    ││
    │  │   Service   │ │   Service   ││
    │  └─────────────┘ └─────────────┘│
    └────────────────┬────────────────┘
                     │
    ┌────────────────▼────────────────┐
    │         Domain Layer            │
    │  ┌─────────────┐ ┌─────────────┐│
    │  │    Movie    │ │   Business  ││
    │  │   Entity    │ │    Rules    ││
    │  └─────────────┘ └─────────────┘│
    └────────────────┬────────────────┘
                     │
    ┌────────────────▼────────────────┐
    │      Repository Port            │
    │         (Interface)             │
    └────────────────┬────────────────┘
                     │
    ┌────────────────▼────────────────┐
    │    In-Memory Repository         │
    │    (Secondary Adapter)          │
    └─────────────────────────────────┘
```

### Key Benefits

- **Multiple Interfaces**: Same business logic accessible via CLI and Web API
- **Testable**: 72 tests covering all layers with high confidence
- **Extensible**: Easy to add new adapters (GraphQL, mobile app, etc.)
- **Domain-Driven**: Rich business model with validation rules
- **CQRS-Influenced**: Separate command and query operations

## 🛠️ Development

### Project Structure

```
├── movie_domain.py          # Core business entities and rules
├── movie_repository.py      # Repository port (interface)
├── in_memory_repository.py  # Repository adapter (implementation)
├── movie_command_service.py # Application layer (commands)
├── movie_query_service.py   # Application layer (queries)
├── movie_cli.py            # CLI primary adapter
├── movie_web_adapter.py    # Web API primary adapter
├── test_*.py               # Comprehensive test suite (72 tests)
├── Dockerfile              # Container configuration
└── docker-compose.yml      # Development environment
```

### Adding New Features

Following the **Shape Up** methodology and hexagonal architecture:

1. **Domain First**: Add business logic to `movie_domain.py`
2. **Application Layer**: Update command/query services
3. **Both Adapters**: Implement feature in CLI and Web API simultaneously
4. **Test Everything**: Feature complete only when both adapters pass tests

### Adding New Adapters

To add a new primary adapter (e.g., GraphQL):

1. Create new adapter file (e.g., `movie_graphql_adapter.py`)
2. Inject same `MovieCommandService` and `MovieQueryService`
3. Map GraphQL operations to service calls
4. Add comprehensive tests

## 🎯 Shape Up Methodology

This project was built using [Shape Up](https://basecamp.com/shapeup) principles:

- **Problem Definition**: Personal movie catalog with clear appetite
- **Shaping**: 2-week cycles with defined boundaries
- **Circuit Breaker**: Working software at each step
- **Risk Management**: TDD eliminated technical unknowns

## 🐳 Docker Commands

```bash
# Start web API
docker-compose up

# Run tests in container
docker-compose run movie-catalog pytest -v

# Use CLI in container
docker-compose --profile cli run movie-cli python movie_cli.py --help

# Clean up
docker-compose down
```

## 📚 Learn More

- **Hexagonal Architecture**: [Alistair Cockburn's original article](https://alistair.cockburn.us/hexagonal-architecture/)
- **Shape Up**: [Basecamp's methodology book](https://basecamp.com/shapeup)
- **Domain-Driven Design**: Clean business logic separated from infrastructure
- **CQRS**: Command Query Responsibility Segregation pattern

## 🤝 Contributing

1. All features must work in both CLI and Web API
2. Comprehensive tests required (aim for >90% coverage)
3. Follow hexagonal architecture principles
4. Document architectural decisions

---

**Built with Python 3.12+ • Flask • pytest • Docker**