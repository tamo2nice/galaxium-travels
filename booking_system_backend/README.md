# Galaxium Booking System

A unified booking system for Galaxium Travels that serves both **REST API** and **MCP (Model Context Protocol)** from a single server.

## Features

- **Dual Protocol Support**: Same business logic exposed via REST and MCP
- **Single Server**: One codebase, one port, both protocols
- **Seat Classes**: Economy, Business, and Galaxium pricing and inventory
- **SQLite Database**: Simple file-based storage for demos
- **Demo Data**: Pre-seeded with space travel flights and users

## Quick Start

### Install Dependencies

```bash
cd booking_system_backend
pip install -r requirements.txt
```

### Run the Server

```bash
python server.py
```

The server starts on port **8080** with:
- REST endpoints at `/flights`, `/book`, `/bookings/{user_id}`, `/cancel/{booking_id}`, `/register`, `/user`
- MCP tools at `/mcp`
- Health check at `/`

## API Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/flights` | List all available flights |
| POST | `/book` | Book a flight |
| GET | `/bookings/{user_id}` | Get user's bookings |
| POST | `/cancel/{booking_id}` | Cancel a booking |
| POST | `/register` | Register a new user |
| GET | `/user?name=...&email=...` | Get user by name and email |

### MCP Tools

| Tool | Description |
|------|-------------|
| `list_flights` | List all available flights |
| `book_flight` | Book a seat on a flight |
| `get_bookings` | Get user's bookings |
| `cancel_booking` | Cancel a booking |
| `register_user` | Register a new user |
| `get_user_id` | Get user by name and email |

## Usage Examples

### REST API

```bash
# List flights
curl http://localhost:8080/flights

# Register a user
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Book a flight in Business class
curl -X POST http://localhost:8080/book \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "name": "Alice", "flight_id": 1, "seat_class": "business"}'

# Get bookings
curl http://localhost:8080/bookings/1

# Cancel a booking
curl -X POST http://localhost:8080/cancel/1
```

### MCP (with Claude Code or MCP Inspector)

Connect to `http://localhost:8080/mcp` and use the available tools:

```
list_flights()
register_user(name="John Doe", email="john@example.com")
book_flight(user_id=1, name="Alice", flight_id=1, seat_class="business")
get_bookings(user_id=1)
cancel_booking(booking_id=1)
```

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_services.py
pytest tests/test_rest.py
```

## Project Structure

```
booking_system/
├── server.py          # Main server - exposes REST & MCP
├── services/          # Business logic layer
│   ├── booking.py     # Booking operations
│   ├── flight.py      # Flight operations
│   └── user.py        # User operations
├── models.py          # SQLAlchemy ORM models
├── schemas.py         # Pydantic request/response schemas
├── db.py              # Database configuration
├── seed.py            # Demo data seeding
├── tests/             # Test suite
│   ├── test_services.py
│   └── test_rest.py
├── requirements.txt
├── Dockerfile
└── pytest.ini
```

## Demo Data

The server seeds the database with:
- **10 users**: Alice, Bob, Charlie, Diana, Eve, Frank, Grace, Heidi, Ivan, Judy
- **10 flights**: Interplanetary routes (Earth, Mars, Moon, Venus, Jupiter, Europa, Pluto)
- **Seat-class pricing**: `economy`, `business`, `galaxium`
- **Seat-class inventory**: separate seat counts per class
- **20 bookings**: Random bookings across users and flights
## Known Issues

- Tests and fixtures still need to be updated to populate the new required seat-class fields on `Flight` and `Booking`.
- Seeded bookings may not consume inventory, which can leave demo seat counts inconsistent.
- Some frontend booking-history views may still rely on the legacy fallback price field instead of `price_paid`.

## Docker

```bash
# Build
docker build -t galaxium-booking .

# Run
docker run -p 8080:8080 galaxium-booking
```

## Architecture

The system uses a **service layer** pattern:

1. **Services** (`services/`) - Pure business logic functions
2. **Server** (`server.py`) - Thin wrappers exposing services via REST and MCP
3. **Models** (`models.py`) - SQLAlchemy ORM definitions, including seat-class fields
4. **Schemas** (`schemas.py`) - Pydantic validation schemas

This architecture ensures:
- Business logic is tested independently of transport layer
- Same validation and error handling for both REST and MCP
- Easy to add new transport layers (GraphQL, gRPC, etc.)
