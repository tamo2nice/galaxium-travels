import { useState } from 'react';
import type { Flight, SeatClass } from '../../types';
import { Card, Button } from '../common';
import { Plane, Clock, DollarSign, Users } from 'lucide-react';
import { formatCurrency, formatDate, formatTime, calculateDuration } from '../../utils/formatters';
import { getSeatClassDisplay } from '../../utils/seatClasses';
import { motion } from 'framer-motion';

interface FlightCardProps {
  flight: Flight;
  onBook: (flightId: number, seatClass: SeatClass) => void;
}

export const FlightCard = ({ flight, onBook }: FlightCardProps) => {
  const [selectedClass, setSelectedClass] = useState<SeatClass>('economy');
  
  const currentClassInfo = flight[selectedClass as keyof Pick<Flight, 'economy' | 'business' | 'galaxium'>];
  const isLowSeats = currentClassInfo.seats_available <= 2;
  const isSoldOut = currentClassInfo.seats_available === 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="h-full flex flex-col">
        {/* Route Header */}
        <div className="flex items-center justify-between mb-4 pb-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cosmic-gradient">
              <Plane className="text-white" size={24} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-star-white">
                {flight.origin} → {flight.destination}
              </h3>
              <p className="text-sm text-star-white/60">
                Flight #{flight.flight_id}
              </p>
            </div>
          </div>
        </div>

        {/* Flight Details */}
        <div className="space-y-3 mb-4 flex-1">
          {/* Departure & Arrival */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-star-white/60 mb-1">Departure</p>
              <p className="text-sm font-medium text-star-white">
                {formatDate(flight.departure_time, 'MMM dd, yyyy')}
              </p>
              <p className="text-lg font-bold text-cosmic-purple">
                {formatTime(flight.departure_time)}
              </p>
            </div>
            <div>
              <p className="text-xs text-star-white/60 mb-1">Arrival</p>
              <p className="text-sm font-medium text-star-white">
                {formatDate(flight.arrival_time, 'MMM dd, yyyy')}
              </p>
              <p className="text-lg font-bold text-cosmic-purple">
                {formatTime(flight.arrival_time)}
              </p>
            </div>
          </div>

          {/* Duration */}
          <div className="flex items-center gap-2 text-star-white/70">
            <Clock size={16} />
            <span className="text-sm">
              Duration: {calculateDuration(flight.departure_time, flight.arrival_time)}
            </span>
          </div>
        </div>

        {/* Seat Class Selection */}
        <div className="border-t border-star-white/10 pt-4 mb-4">
          <h4 className="text-sm font-semibold text-star-white/70 mb-3">
            Select Seat Class
          </h4>
          
          <div className="grid grid-cols-3 gap-2 mb-4">
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
                    {formatCurrency(classInfo.price)}
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

          {/* Selected Class Details */}
          <div className="bg-deep-space/50 p-3 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-star-white/70">
                  {getSeatClassDisplay(selectedClass).description}
                </p>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 justify-end">
                  <DollarSign size={16} className="text-alien-green" />
                  <p className="text-2xl font-bold text-star-white">
                    {formatCurrency(currentClassInfo.price)}
                  </p>
                </div>
                <div className="flex items-center gap-1 justify-end mt-1">
                  <Users size={14} className={isLowSeats ? 'text-solar-orange' : 'text-star-white/60'} />
                  <p className={`text-xs ${isLowSeats ? 'text-solar-orange font-semibold' : 'text-star-white/60'}`}>
                    {currentClassInfo.seats_available} available
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Book Button */}
        <Button
          onClick={() => onBook(flight.flight_id, selectedClass)}
          disabled={isSoldOut}
          className="w-full"
        >
          {isSoldOut 
            ? 'Sold Out' 
            : `Book ${getSeatClassDisplay(selectedClass).label} Class`
          }
        </Button>
      </Card>
    </motion.div>
  );
};

// Made with Bob
