/**
 * Service for interacting with the backend API
 */

// API URL - configurable via environment variable
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

// Log the configuration on startup
console.log(`API Service configured with URL: ${API_URL}`);

/**
 * Check if the backend server is available
 * @returns {Promise<boolean>} - True if server is available
 */
export const checkServerStatus = async () => {
  try {
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return response.ok;
  } catch (error) {
    console.error('Error checking server status:', error);
    return false;
  }
};

/**
 * Process itinerary text using the backend API
 * @param {string} text - The itinerary text to process
 * @returns {Promise<Object>} - Processed calendar data
 */
export const processItinerary = async (text) => {
  try {
    const response = await fetch(`${API_URL}/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('API error:', errorData);
      return {
        success: false,
        message: `API error: ${errorData.message || 'Unknown error'}`,
      };
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error processing itinerary with API:', error);
    return {
      success: false,
      message: `Failed to process itinerary: ${error.message}`,
    };
  }
};
