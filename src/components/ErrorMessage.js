import React from 'react';

/**
 * Error message component with suggestions
 */
function ErrorMessage({ message, onDismiss }) {
  // Get suggestion based on error message
  const getSuggestion = () => {
    if (message.includes('Ollama')) {
      return 'Make sure Ollama is running locally or try using the backend server.';
    } else if (message.includes('extract')) {
      return 'Try using one of the sample itineraries to see the expected format.';
    } else if (message.includes('server')) {
      return 'Check your internet connection or try again later.';
    } else {
      return 'Try using a different itinerary format or one of the samples.';
    }
  };
  
  return (
    <div className="error-message" role="alert">
      <div className="error-content">
        <div className="error-icon">⚠️</div>
        <div className="error-text">
          <h3>Error</h3>
          <p>{message}</p>
          <p className="error-suggestion">{getSuggestion()}</p>
        </div>
        <button 
          className="error-dismiss" 
          onClick={onDismiss}
          aria-label="Dismiss error"
        >
          ×
        </button>
      </div>
    </div>
  );
}

export default ErrorMessage;
