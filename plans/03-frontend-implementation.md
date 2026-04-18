# 座席クラス機能実装計画 - フロントエンド

## 1. 型定義の更新

### 1.1 types/index.tsの更新

```typescript
// 座席クラス情報
export interface SeatClassInfo {
  price: number;
  seats_available: number;
}

// 座席クラスの型
export type SeatClass = 'economy' | 'business' | 'galaxium';

// Flightインターフェースの更新
export interface Flight {
  flight_id: number;
  origin: string;
  destination: string;
  departure_time: string;
  arrival_time: string;
  
  // 後方互換性のため保持
  price: number;
  seats_available: number;
  
  // 座席クラス別情報
  economy: SeatClassInfo;
  business: SeatClassInfo;
  galaxium: SeatClassInfo;
}

// Bookingインターフェースの更新
export interface Booking {
  booking_id: number;
  user_id: number;
  flight_id: number;
  status: 'booked' | 'cancelled' | 'completed';
  booking_time: string;
  seat_class: SeatClass;
  price_paid: number;
}

// BookingRequestの更新
export interface BookingRequest {
  user_id: number;
  name: string;
  flight_id: number;
  seat_class?: SeatClass;  // オプショナル、デフォルトはeconomy
}

// 座席クラス表示用の情報
export interface SeatClassDisplay {
  value: SeatClass;
  label: string;
  description: string;
  icon: string;
  color: string;
}
```

### 1.2 座席クラス定数の定義

```typescript
// utils/seatClasses.ts
export const SEAT_CLASSES: Record<SeatClass, SeatClassDisplay> = {
  economy: {
    value: 'economy',
    label: 'Economy',
    description: 'Standard seating with essential amenities',
    icon: '🪑',
    color: 'text-blue-400'
  },
  business: {
    value: 'business',
    label: 'Business',
    description: 'Enhanced comfort with premium services',
    icon: '💼',
    color: 'text-purple-400'
  },
  galaxium: {
    value: 'galaxium',
    label: 'Galaxium',
    description: 'Ultimate luxury with exclusive amenities',
    icon: '⭐',
    color: 'text-yellow-400'
  }
};

export const getSeatClassDisplay = (seatClass: SeatClass): SeatClassDisplay => {
  return SEAT_CLASSES[seatClass];
};
```

## 2. コンポーネントの更新

### 2.1 FlightCard.tsxの更新

```typescript
// components/flights/FlightCard.tsx

interface FlightCardProps {
  flight: Flight;
  onBook: (flightId: number, seatClass: SeatClass) => void;
}

export const FlightCard = ({ flight, onBook }: FlightCardProps) => {
  const [selectedClass, setSelectedClass] = useState<SeatClass>('economy');
  const [showClassSelector, setShowClassSelector] = useState(false);

  const currentClassInfo = flight[selectedClass];

  return (
    <Card className="hover:border-cosmic-purple transition-all">
      {/* 既存のフライト情報 */}
      <div className="space-y-4">
        {/* Origin/Destination */}
        <div>...</div>
        
        {/* 座席クラス選択 */}
        <div className="border-t border-star-white/10 pt-4">
          <h4 className="text-sm font-semibold text-star-white/70 mb-3">
            Select Seat Class
          </h4>
          
          <div className="grid grid-cols-3 gap-2">
            {(['economy', 'business', 'galaxium'] as SeatClass[]).map((seatClass) => {
              const classInfo = flight[seatClass];
              const display = getSeatClassDisplay(seatClass);
              const isAvailable = classInfo.seats_available > 0;
              const isSelected = selectedClass === seatClass;
              
              return (
                <button
                  key={seatClass}
                  onClick={() => setSelectedClass(seatClass)}
                  disabled={!isAvailable}
                  className={`
                    p-3 rounded-lg border-2 transition-all
                    ${isSelected 
                      ? 'border-cosmic-purple bg-cosmic-purple/20' 
                      : 'border-star-white/20 hover:border-star-white/40'
                    }
                    ${!isAvailable && 'opacity-50 cursor-not-allowed'}
                  `}
                >
                  <div className="text-2xl mb-1">{display.icon}</div>
                  <div className={`text-xs font-semibold ${display.color}`}>
                    {display.label}
                  </div>
                  <div className="text-xs text-star-white/60 mt-1">
                    ${classInfo.price.toLocaleString()}
                  </div>
                  <div className="text-xs text-star-white/40 mt-1">
                    {isAvailable 
                      ? `${classInfo.seats_available} seats` 
                      : 'Sold out'
                    }
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* 選択されたクラスの詳細 */}
        <div className="bg-deep-space/50 p-3 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-star-white/70">
                {getSeatClassDisplay(selectedClass).description}
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-nebula-pink">
                ${currentClassInfo.price.toLocaleString()}
              </p>
              <p className="text-xs text-star-white/60">
                {currentClassInfo.seats_available} seats available
              </p>
            </div>
          </div>
        </div>

        {/* Book button */}
        <Button
          onClick={() => onBook(flight.flight_id, selectedClass)}
          disabled={currentClassInfo.seats_available === 0}
          className="w-full"
        >
          {currentClassInfo.seats_available === 0 
            ? 'Sold Out' 
            : `Book ${getSeatClassDisplay(selectedClass).label} Class`
          }
        </Button>
      </div>
    </Card>
  );
};
```

### 2.2 BookingModal.tsxの更新

```typescript
// components/bookings/BookingModal.tsx

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  flight: Flight | null;
  seatClass: SeatClass;
  onConfirm: (seatClass: SeatClass) => void;
}

export const BookingModal = ({ 
  isOpen, 
  onClose, 
  flight, 
  seatClass,
  onConfirm 
}: BookingModalProps) => {
  if (!flight) return null;

  const classInfo = flight[seatClass];
  const display = getSeatClassDisplay(seatClass);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Confirm Booking">
      <div className="space-y-4">
        {/* Flight details */}
        <div className="bg-deep-space/50 p-4 rounded-lg">
          <h3 className="font-semibold text-lg mb-2">
            {flight.origin} → {flight.destination}
          </h3>
          <p className="text-sm text-star-white/70">
            {formatDateTime(flight.departure_time)}
          </p>
        </div>

        {/* Seat class details */}
        <div className="border-2 border-cosmic-purple/50 p-4 rounded-lg">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-3xl">{display.icon}</span>
            <div>
              <h4 className={`font-semibold ${display.color}`}>
                {display.label} Class
              </h4>
              <p className="text-xs text-star-white/60">
                {display.description}
              </p>
            </div>
          </div>
          
          <div className="mt-3 pt-3 border-t border-star-white/10">
            <div className="flex justify-between items-center">
              <span className="text-star-white/70">Price:</span>
              <span className="text-2xl font-bold text-nebula-pink">
                ${classInfo.price.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Amenities based on class */}
        <div className="bg-deep-space/30 p-4 rounded-lg">
          <h4 className="text-sm font-semibold mb-2">Included Amenities</h4>
          <ul className="text-sm text-star-white/70 space-y-1">
            {getAmenitiesForClass(seatClass).map((amenity, index) => (
              <li key={index} className="flex items-center gap-2">
                <span className="text-cosmic-purple">✓</span>
                {amenity}
              </li>
            ))}
          </ul>
        </div>

        {/* Confirm button */}
        <Button 
          onClick={() => onConfirm(seatClass)} 
          className="w-full"
        >
          Confirm Booking - ${classInfo.price.toLocaleString()}
        </Button>
      </div>
    </Modal>
  );
};

// Helper function for amenities
const getAmenitiesForClass = (seatClass: SeatClass): string[] => {
  const amenities = {
    economy: [
      'Standard seating',
      'In-flight entertainment',
      'Complimentary snacks',
      '1 checked bag'
    ],
    business: [
      'Priority boarding',
      'Extra legroom',
      'Premium meals',
      'Lounge access',
      '2 checked bags',
      'Priority baggage handling'
    ],
    galaxium: [
      'Private cabin',
      'Luxury bedding',
      'Gourmet dining',
      'Personal concierge',
      'Unlimited baggage',
      'Spa services',
      'Exclusive lounge access'
    ]
  };
  return amenities[seatClass];
};
```

### 2.3 BookingCard.tsxの更新

```typescript
// components/bookings/BookingCard.tsx

export const BookingCard = ({ booking, flight }: BookingCardProps) => {
  const display = getSeatClassDisplay(booking.seat_class);
  
  return (
    <Card>
      <div className="space-y-3">
        {/* Flight info */}
        <div>...</div>

        {/* Seat class badge */}
        <div className="flex items-center gap-2">
          <span className="text-xl">{display.icon}</span>
          <span className={`text-sm font-semibold ${display.color}`}>
            {display.label} Class
          </span>
        </div>

        {/* Price paid */}
        <div className="flex justify-between items-center pt-2 border-t border-star-white/10">
          <span className="text-sm text-star-white/70">Price Paid:</span>
          <span className="text-lg font-bold text-nebula-pink">
            ${booking.price_paid.toLocaleString()}
          </span>
        </div>

        {/* Status and actions */}
        <div>...</div>
      </div>
    </Card>
  );
};
```

## 3. APIサービスの更新

### 3.1 services/api.tsの更新

```typescript
// services/api.ts

export const bookFlight = async (
  userId: number,
  name: string,
  flightId: number,
  seatClass: SeatClass = 'economy'
): Promise<Booking | ErrorResponse> => {
  try {
    const response = await api.post<Booking>('/bookings', {
      user_id: userId,
      name,
      flight_id: flightId,
      seat_class: seatClass
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return error.response.data as ErrorResponse;
    }
    throw error;
  }
};
```

## 4. ページコンポーネントの更新

### 4.1 Flights.tsxの更新

```typescript
// pages/Flights.tsx

export const Flights = () => {
  const [selectedFlight, setSelectedFlight] = useState<Flight | null>(null);
  const [selectedSeatClass, setSelectedSeatClass] = useState<SeatClass>('economy');
  const [showBookingModal, setShowBookingModal] = useState(false);

  const handleBookClick = (flightId: number, seatClass: SeatClass) => {
    const flight = flights.find(f => f.flight_id === flightId);
    if (flight) {
      setSelectedFlight(flight);
      setSelectedSeatClass(seatClass);
      
      if (user) {
        setShowBookingModal(true);
      } else {
        setShowUserModal(true);
      }
    }
  };

  const handleConfirmBooking = async (seatClass: SeatClass) => {
    if (!user || !selectedFlight) return;

    setIsBooking(true);
    try {
      const result = await bookFlight(
        user.user_id,
        user.name,
        selectedFlight.flight_id,
        seatClass
      );

      if (isErrorResponse(result)) {
        toast.error(result.details || result.error);
      } else {
        toast.success(`Successfully booked ${getSeatClassDisplay(seatClass).label} class!`);
        setShowBookingModal(false);
        // Refresh flights
        fetchFlights();
      }
    } catch (error) {
      toast.error('Failed to book flight');
    } finally {
      setIsBooking(false);
    }
  };

  return (
    <div>
      {/* Flight list */}
      <div className="grid gap-6">
        {flights.map(flight => (
          <FlightCard
            key={flight.flight_id}
            flight={flight}
            onBook={handleBookClick}
          />
        ))}
      </div>

      {/* Booking modal */}
      <BookingModal
        isOpen={showBookingModal}
        onClose={() => setShowBookingModal(false)}
        flight={selectedFlight}
        seatClass={selectedSeatClass}
        onConfirm={handleConfirmBooking}
      />
    </div>
  );
};
```

## 5. フィルタリング機能の拡張（オプション）

### 5.1 FlightFiltersの更新

```typescript
export interface FlightFilters {
  origin?: string;
  destination?: string;
  minPrice?: number;
  maxPrice?: number;
  searchTerm?: string;
  seatClass?: SeatClass;  // 新しいフィルター
  minSeats?: number;
}

// フィルタリングロジック
const filterFlights = (flights: Flight[], filters: FlightFilters): Flight[] => {
  return flights.filter(flight => {
    // 既存のフィルター
    if (filters.origin && flight.origin !== filters.origin) return false;
    if (filters.destination && flight.destination !== filters.destination) return false;
    
    // 座席クラスフィルター
    if (filters.seatClass) {
      const classInfo = flight[filters.seatClass];
      if (filters.minPrice && classInfo.price < filters.minPrice) return false;
      if (filters.maxPrice && classInfo.price > filters.maxPrice) return false;
      if (filters.minSeats && classInfo.seats_available < filters.minSeats) return false;
    } else {
      // 座席クラスが指定されていない場合はeconomyを使用
      if (filters.minPrice && flight.economy.price < filters.minPrice) return false;
      if (filters.maxPrice && flight.economy.price > filters.maxPrice) return false;
    }
    
    return true;
  });
};
```

## 6. スタイリングの追加

### 6.1 座席クラス用のTailwindカラー

```typescript
// tailwind.config.js に追加
module.exports = {
  theme: {
    extend: {
      colors: {
        'seat-economy': '#3b82f6',
        'seat-business': '#8b5cf6',
        'seat-galaxium': '#fbbf24',
      }
    }
  }
}
```

## 7. 実装順序

1. **types/index.ts**: 型定義を更新
2. **utils/seatClasses.ts**: 座席クラス定数を作成
3. **services/api.ts**: API関数を更新
4. **components/flights/FlightCard.tsx**: 座席クラス選択UIを追加
5. **components/bookings/BookingModal.tsx**: 座席クラス情報を表示
6. **components/bookings/BookingCard.tsx**: 予約済み座席クラスを表示
7. **pages/Flights.tsx**: 予約フローを更新
8. **pages/MyBookings.tsx**: 座席クラス情報を表示
9. **フィルター機能**: 座席クラスフィルターを追加（オプション）

## 8. テスト項目

### 8.1 手動テスト
- [ ] 各座席クラスの価格が正しく表示される
- [ ] 座席クラスを選択して予約できる
- [ ] 満席の座席クラスは予約できない
- [ ] 予約履歴に座席クラスと支払額が表示される
- [ ] 座席クラスごとに座席数が正しく減少する
- [ ] キャンセル時に座席数が正しく復元される

### 8.2 エッジケース
- [ ] 座席クラスを指定しない場合はeconomyになる
- [ ] 無効な座席クラスを指定した場合のエラーハンドリング
- [ ] 複数ユーザーが同時に最後の座席を予約しようとした場合

## 9. 注意事項

- **後方互換性**: 既存のコードが`flight.price`と`flight.seats_available`を使用している場合でも動作する
- **レスポンシブデザイン**: 座席クラス選択UIはモバイルでも使いやすくする
- **アクセシビリティ**: 座席クラスの選択はキーボードでも操作可能にする
- **パフォーマンス**: 座席クラス情報の表示で不要な再レンダリングを避ける