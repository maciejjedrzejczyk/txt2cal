import React from 'react';
import { sampleItineraries } from '../utils/testUtils';

/**
 * Button component for loading sample itinerary text
 */
function SampleButton({ type, onSelect }) {
  const handleClick = () => {
    if (sampleItineraries[type]) {
      onSelect(sampleItineraries[type]);
    }
  };

  const getButtonLabel = () => {
    switch (type) {
      case 'flight':
        return 'Flight Sample';
      case 'hotel':
        return 'Hotel Sample';
      case 'carRental':
        return 'Car Rental Sample';
      case 'restaurant':
        return 'Restaurant Sample';
      case 'complex':
        return 'Complex Itinerary';
      default:
        return 'Sample';
    }
  };

  return (
    <button 
      className={`sample-button sample-${type}`} 
      onClick={handleClick}
      title={`Load a sample ${type} itinerary`}
    >
      {getButtonLabel()}
    </button>
  );
}

export default SampleButton;
