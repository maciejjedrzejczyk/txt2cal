import React from 'react';

/**
 * Loading spinner component with progress messages
 */
function LoadingSpinner() {
  return (
    <div className="loading-container" aria-live="polite">
      <div className="loading-spinner">
        <div className="spinner"></div>
      </div>
      <div className="loading-message">
        <p>Processing your itinerary...</p>
        <p className="loading-detail">Extracting dates, times, and details</p>
      </div>
    </div>
  );
}

export default LoadingSpinner;
