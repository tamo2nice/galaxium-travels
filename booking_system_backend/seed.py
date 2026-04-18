from models import Base, User, Flight, Booking
from db import engine, SessionLocal
from datetime import datetime, timedelta
import random

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Clear existing data
    db.query(Booking).delete()
    db.query(User).delete()
    db.query(Flight).delete()
    db.commit()
    # Add demo users
    users = [
        User(name="Alice", email="alice@example.com"),
        User(name="Bob", email="bob@example.com"),
        User(name="Charlie", email="charlie@galaxium.com"),
        User(name="Diana", email="diana@moonmail.com"),
        User(name="Eve", email="eve@marsmail.com"),
        User(name="Frank", email="frank@venusmail.com"),
        User(name="Grace", email="grace@jupiter.com"),
        User(name="Heidi", email="heidi@europa.com"),
        User(name="Ivan", email="ivan@asteroidbelt.com"),
        User(name="Judy", email="judy@pluto.com"),
    ]
    db.add_all(users)
    db.commit()
    # Add demo flights with seat classes
    flight_data = [
        {"origin": "Earth", "destination": "Mars", "departure_time": "2099-01-01T09:00:00Z", "arrival_time": "2099-01-01T17:00:00Z", "base_price": 1000000, "total_seats": 15},
        {"origin": "Earth", "destination": "Moon", "departure_time": "2099-01-02T10:00:00Z", "arrival_time": "2099-01-02T14:00:00Z", "base_price": 500000, "total_seats": 10},
        {"origin": "Mars", "destination": "Earth", "departure_time": "2099-01-03T12:00:00Z", "arrival_time": "2099-01-03T20:00:00Z", "base_price": 950000, "total_seats": 20},
        {"origin": "Venus", "destination": "Earth", "departure_time": "2099-01-04T08:00:00Z", "arrival_time": "2099-01-04T18:00:00Z", "base_price": 1200000, "total_seats": 8},
        {"origin": "Jupiter", "destination": "Europa", "departure_time": "2099-01-05T15:00:00Z", "arrival_time": "2099-01-05T19:00:00Z", "base_price": 2000000, "total_seats": 6},
        {"origin": "Earth", "destination": "Venus", "departure_time": "2099-01-06T07:00:00Z", "arrival_time": "2099-01-06T15:00:00Z", "base_price": 1100000, "total_seats": 12},
        {"origin": "Moon", "destination": "Mars", "departure_time": "2099-01-07T11:00:00Z", "arrival_time": "2099-01-07T19:00:00Z", "base_price": 800000, "total_seats": 18},
        {"origin": "Mars", "destination": "Jupiter", "departure_time": "2099-01-08T13:00:00Z", "arrival_time": "2099-01-08T23:00:00Z", "base_price": 2500000, "total_seats": 8},
        {"origin": "Europa", "destination": "Earth", "departure_time": "2099-01-09T09:00:00Z", "arrival_time": "2099-01-09T21:00:00Z", "base_price": 3000000, "total_seats": 10},
        {"origin": "Earth", "destination": "Pluto", "departure_time": "2099-01-10T06:00:00Z", "arrival_time": "2099-01-11T06:00:00Z", "base_price": 5000000, "total_seats": 5},
    ]
    
    flights = []
    for data in flight_data:
        base_price = data["base_price"]
        total_seats = data["total_seats"]
        
        # 座席クラス別の価格設定
        economy_price = base_price
        business_price = int(base_price * 2)
        galaxium_price = int(base_price * 3.5)
        
        # 座席クラス別の座席数配分 (60% Economy, 30% Business, 10% Galaxium)
        economy_seats = int(total_seats * 0.6)
        business_seats = int(total_seats * 0.3)
        galaxium_seats = max(1, int(total_seats * 0.1))  # 最低1席
        
        flights.append(Flight(
            origin=data["origin"],
            destination=data["destination"],
            departure_time=data["departure_time"],
            arrival_time=data["arrival_time"],
            price=economy_price,  # 後方互換性
            seats_available=economy_seats,  # 後方互換性
            economy_price=economy_price,
            business_price=business_price,
            galaxium_price=galaxium_price,
            economy_seats=economy_seats,
            business_seats=business_seats,
            galaxium_seats=galaxium_seats
        ))
    db.add_all(flights)
    db.commit()
    # Add demo bookings with seat classes
    user_ids = [user.user_id for user in db.query(User).all()]
    flights_list = db.query(Flight).all()
    statuses = ["booked", "cancelled", "completed"]
    seat_classes = ["economy", "business", "galaxium"]
    bookings = []
    now = datetime.utcnow()
    
    for i in range(20):
        user_id = random.choice(user_ids)
        flight = random.choice(flights_list)
        status = random.choice(statuses)
        
        # 利用可能な座席クラスから選択（在庫がある場合のみ）
        available_classes = []
        if flight.economy_seats > 0:
            available_classes.append("economy")
        if flight.business_seats > 0:
            available_classes.append("business")
        if flight.galaxium_seats > 0:
            available_classes.append("galaxium")
        
        # 在庫がない場合はスキップ
        if not available_classes:
            continue
            
        seat_class = random.choice(available_classes)
        booking_time = (now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))).isoformat() + "Z"
        
        # 座席クラスに応じた価格を取得
        if seat_class == "economy":
            price_paid = flight.economy_price
        elif seat_class == "business":
            price_paid = flight.business_price
        else:  # galaxium
            price_paid = flight.galaxium_price
        
        # 予約がアクティブ（booked）の場合のみ在庫を減らす
        if status == "booked":
            if seat_class == "economy":
                flight.economy_seats -= 1
            elif seat_class == "business":
                flight.business_seats -= 1
            else:  # galaxium
                flight.galaxium_seats -= 1
            
            # 後方互換性のため、economyの場合はseats_availableも更新
            if seat_class == "economy":
                flight.seats_available -= 1
        
        bookings.append(Booking(
            user_id=user_id,
            flight_id=flight.flight_id,
            status=status,
            booking_time=booking_time,
            seat_class=seat_class,
            price_paid=price_paid
        ))
    
    db.add_all(bookings)
    db.commit()
    db.close()
    print("Database seeded with elaborate demo data!")

if __name__ == "__main__":
    seed() 