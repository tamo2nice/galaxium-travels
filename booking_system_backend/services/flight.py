from sqlalchemy.orm import Session
from models import Flight
from schemas import FlightOut, SeatClassInfo


def list_flights(db: Session) -> list[FlightOut]:
    """List all available flights with seat class information."""
    flights = db.query(Flight).all()
    result = []
    for flight in flights:
        flight_dict = {
            'flight_id': flight.flight_id,
            'origin': flight.origin,
            'destination': flight.destination,
            'departure_time': flight.departure_time,
            'arrival_time': flight.arrival_time,
            'price': flight.economy_price,  # 後方互換性
            'seats_available': flight.economy_seats,  # 後方互換性
            'economy': {
                'price': flight.economy_price,
                'seats_available': flight.economy_seats
            },
            'business': {
                'price': flight.business_price,
                'seats_available': flight.business_seats
            },
            'galaxium': {
                'price': flight.galaxium_price,
                'seats_available': flight.galaxium_seats
            }
        }
        result.append(FlightOut(**flight_dict))
    return result
