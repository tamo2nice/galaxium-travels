# 座席クラス機能実装計画 - バックエンド

## 1. データベーススキーマ変更

### 1.1 Flightモデルの拡張

**現在の構造:**
```python
class Flight(Base):
    __tablename__ = 'flights'
    flight_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(String, nullable=False)
    arrival_time = Column(String, nullable=False)
    price = Column(Integer, nullable=False)  # 後方互換性のため保持
    seats_available = Column(Integer, nullable=False)  # 後方互換性のため保持
```

**新しい構造:**
```python
class Flight(Base):
    __tablename__ = 'flights'
    flight_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(String, nullable=False)
    arrival_time = Column(String, nullable=False)
    
    # 後方互換性のため保持（Economyクラスの値を参照）
    price = Column(Integer, nullable=False)
    seats_available = Column(Integer, nullable=False)
    
    # 座席クラス別の価格
    economy_price = Column(Integer, nullable=False)
    business_price = Column(Integer, nullable=False)
    galaxium_price = Column(Integer, nullable=False)
    
    # 座席クラス別の座席数
    economy_seats = Column(Integer, nullable=False)
    business_seats = Column(Integer, nullable=False)
    galaxium_seats = Column(Integer, nullable=False)
```

### 1.2 Bookingモデルの拡張

**現在の構造:**
```python
class Booking(Base):
    __tablename__ = 'bookings'
    booking_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.flight_id'), nullable=False)
    status = Column(String, nullable=False)
    booking_time = Column(String, nullable=False)
```

**新しい構造:**
```python
class Booking(Base):
    __tablename__ = 'bookings'
    booking_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.flight_id'), nullable=False)
    status = Column(String, nullable=False)
    booking_time = Column(String, nullable=False)
    seat_class = Column(String, nullable=False, default='economy')  # 'economy', 'business', 'galaxium'
    price_paid = Column(Integer, nullable=False)  # 予約時の実際の支払額
```

## 2. Pydanticスキーマの更新

### 2.1 FlightOutスキーマ

```python
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
```

### 2.2 BookingRequestスキーマ

```python
class BookingRequest(BaseModel):
    user_id: int
    name: str
    flight_id: int
    seat_class: str = 'economy'  # デフォルトはeconomy
    
    @validator('seat_class')
    def validate_seat_class(cls, v):
        allowed = ['economy', 'business', 'galaxium']
        if v not in allowed:
            raise ValueError(f'seat_class must be one of {allowed}')
        return v
```

### 2.3 BookingOutスキーマ

```python
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
```

## 3. サービス層の変更

### 3.1 flight.pyの更新

```python
def list_flights(db: Session) -> list[FlightOut]:
    """全フライトを取得し、座席クラス情報を含める"""
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
```

### 3.2 booking.pyの更新

```python
def book_flight(db: Session, user_id: int, name: str, flight_id: int, seat_class: str = 'economy') -> BookingOut | ErrorResponse:
    """座席クラスを指定してフライトを予約"""
    
    # フライト存在確認
    flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
    if not flight:
        return ErrorResponse(
            error="Flight not found",
            error_code="FLIGHT_NOT_FOUND",
            details=f"Flight {flight_id} does not exist"
        )
    
    # 座席クラスの検証
    if seat_class not in ['economy', 'business', 'galaxium']:
        return ErrorResponse(
            error="Invalid seat class",
            error_code="INVALID_SEAT_CLASS",
            details=f"Seat class must be one of: economy, business, galaxium"
        )
    
    # 座席数と価格の取得
    seats_field = f"{seat_class}_seats"
    price_field = f"{seat_class}_price"
    
    available_seats = getattr(flight, seats_field)
    price = getattr(flight, price_field)
    
    # 座席の空き確認
    if available_seats < 1:
        return ErrorResponse(
            error="No seats available",
            error_code="NO_SEATS_AVAILABLE",
            details=f"No {seat_class} class seats available on this flight"
        )
    
    # ユーザー確認（既存のロジック）
    user = db.query(User).filter(User.user_id == user_id, User.name == name).first()
    if not user:
        # 既存のエラーハンドリング
        ...
    
    # 座席数を減らす
    setattr(flight, seats_field, available_seats - 1)
    
    # 後方互換性のためpriceとseats_availableも更新（economyの値を使用）
    flight.price = flight.economy_price
    flight.seats_available = flight.economy_seats
    
    # 予約作成
    new_booking = Booking(
        user_id=user_id,
        flight_id=flight_id,
        status="booked",
        booking_time=datetime.utcnow().isoformat(),
        seat_class=seat_class,
        price_paid=price
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return BookingOut.model_validate(new_booking)


def cancel_booking(db: Session, booking_id: int) -> BookingOut | ErrorResponse:
    """予約をキャンセルし、座席を復元"""
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        return ErrorResponse(...)
    
    if booking.status == "cancelled":
        return ErrorResponse(...)
    
    # 座席を復元
    flight = db.query(Flight).filter(Flight.flight_id == booking.flight_id).first()
    if flight:
        seats_field = f"{booking.seat_class}_seats"
        current_seats = getattr(flight, seats_field)
        setattr(flight, seats_field, current_seats + 1)
        
        # 後方互換性の更新
        flight.price = flight.economy_price
        flight.seats_available = flight.economy_seats
    
    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return BookingOut.model_validate(booking)
```

## 4. データマイグレーション戦略

### 4.1 既存データの処理

```python
def migrate_existing_data(db: Session):
    """既存のフライトとブッキングデータを新しいスキーマに移行"""
    
    # 全フライトを取得
    flights = db.query(Flight).all()
    
    for flight in flights:
        # 既存のpriceをeconomy_priceとして使用
        flight.economy_price = flight.price
        flight.business_price = int(flight.price * 2)
        flight.galaxium_price = int(flight.price * 3.5)
        
        # 既存のseats_availableを分配
        total_seats = flight.seats_available
        flight.economy_seats = int(total_seats * 0.6)  # 60%
        flight.business_seats = int(total_seats * 0.3)  # 30%
        flight.galaxium_seats = int(total_seats * 0.1)  # 10%
        
        # 後方互換性フィールドを更新
        flight.price = flight.economy_price
        flight.seats_available = flight.economy_seats
    
    # 全予約を取得
    bookings = db.query(Booking).all()
    
    for booking in bookings:
        # 既存の予約は全てeconomyとして扱う
        booking.seat_class = 'economy'
        # price_paidは対応するフライトのeconomy_priceを使用
        flight = db.query(Flight).filter(Flight.flight_id == booking.flight_id).first()
        if flight:
            booking.price_paid = flight.economy_price
    
    db.commit()
```

## 5. REST APIエンドポイントの更新

### 5.1 予約エンドポイント

```python
@app.post("/bookings", response_model=BookingOut | ErrorResponse)
async def create_booking(request: BookingRequest, db: Session = Depends(get_db)):
    """座席クラスを指定して予約を作成"""
    result = booking.book_flight(
        db, 
        request.user_id, 
        request.name, 
        request.flight_id,
        request.seat_class  # 新しいパラメータ
    )
    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=400, content=result.model_dump())
    return result
```

## 6. テストの更新

### 6.1 新しいテストケース

```python
def test_book_flight_with_seat_class(db_session):
    """座席クラスを指定した予約のテスト"""
    # Business classの予約
    result = booking.book_flight(db_session, 1, "Alice", 1, "business")
    assert isinstance(result, BookingOut)
    assert result.seat_class == "business"
    assert result.price_paid > 0
    
    # Galaxium classの予約
    result = booking.book_flight(db_session, 1, "Alice", 1, "galaxium")
    assert isinstance(result, BookingOut)
    assert result.seat_class == "galaxium"

def test_no_seats_available_for_class(db_session):
    """特定クラスの座席が満席の場合のテスト"""
    # Galaxium classの座席を全て予約
    flight = db_session.query(Flight).first()
    flight.galaxium_seats = 0
    db_session.commit()
    
    result = booking.book_flight(db_session, 1, "Alice", flight.flight_id, "galaxium")
    assert isinstance(result, ErrorResponse)
    assert result.error_code == "NO_SEATS_AVAILABLE"
```

## 7. 実装順序

1. **models.py**: Flightモデルに新しいカラムを追加
2. **models.py**: Bookingモデルに新しいカラムを追加
3. **schemas.py**: 新しいスキーマを定義
4. **マイグレーション**: 既存データを新しいスキーマに移行
5. **services/flight.py**: list_flights関数を更新
6. **services/booking.py**: book_flight関数を更新
7. **services/booking.py**: cancel_booking関数を更新
8. **server.py**: エンドポイントを更新（必要に応じて）
9. **seed.py**: 新しいデータ構造でシードデータを生成
10. **tests/**: テストケースを追加・更新

## 8. 注意事項

- **後方互換性**: `price`と`seats_available`フィールドは削除せず、常にeconomyクラスの値を参照
- **デフォルト値**: 座席クラスを指定しない場合はeconomyを使用
- **バリデーション**: 座席クラスは'economy', 'business', 'galaxium'のみ許可
- **価格の一貫性**: 予約時の価格を`price_paid`に保存し、後で価格が変更されても影響を受けないようにする