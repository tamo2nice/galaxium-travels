import type { SeatClass, SeatClassDisplay } from '../types';

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

export const getAmenitiesForClass = (seatClass: SeatClass): string[] => {
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

// Made with Bob
