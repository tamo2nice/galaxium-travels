from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class SeatClassInfo(BaseModel):
    """座席クラス情報"""
    price: int
    seats_available: int


class FlightOut(BaseModel):
    flight_id: int
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    
    # 後方互換性のため保持
    price: int
    seats_available: int
    
    # 座席クラス別情報
    economy: SeatClassInfo
    business: SeatClassInfo
    galaxium: SeatClassInfo

    class Config:
        from_attributes = True


class BookingRequest(BaseModel):
    user_id: int
    name: str
    flight_id: int
    seat_class: str = 'economy'
    
    @field_validator('seat_class')
    @classmethod
    def validate_seat_class(cls, v: str) -> str:
        allowed = ['economy', 'business', 'galaxium']
        if v not in allowed:
            raise ValueError(f'seat_class must be one of {allowed}')
        return v


class BookingOut(BaseModel):
    booking_id: int
    user_id: int
    flight_id: int
    status: str
    booking_time: str
    seat_class: str
    price_paid: int

    class Config:
        from_attributes = True


class UserRegistration(BaseModel):
    name: str
    email: EmailStr


class UserOut(BaseModel):
    user_id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: str
    details: Optional[str] = None
