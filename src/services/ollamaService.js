/**
 * Service for interacting with the local Ollama API
 */

// Ollama API URL - configurable via environment variable
const OLLAMA_API_URL = process.env.REACT_APP_OLLAMA_API_URL || 'http://localhost:11434/api';
const MODEL = process.env.REACT_APP_OLLAMA_MODEL || 'llama3.2';

// Log the configuration on startup
console.log(`Ollama Service configured with API URL: ${OLLAMA_API_URL}`);
console.log(`Using model: ${MODEL}`);

/**
 * Check if Ollama is available locally
 * @returns {Promise<boolean>} - True if Ollama is available
 */
export const checkOllamaStatus = async () => {
  try {
    const response = await fetch(`${OLLAMA_API_URL}/tags`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return response.ok;
  } catch (error) {
    console.error('Error checking Ollama status:', error);
    return false;
  }
};

/**
 * Process itinerary text using local Ollama
 * @param {string} text - The itinerary text to process
 * @returns {Promise<Object>} - Processed calendar data
 */
export const processItinerary = async (text) => {
  try {
    // Create prompt for Ollama
    const prompt = createPrompt(text);
    
    // Call Ollama API
    const response = await fetch(`${OLLAMA_API_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: MODEL,
        prompt,
        stream: false,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Ollama API error:', errorData);
      return {
        success: false,
        message: `Ollama API error: ${errorData.error || 'Unknown error'}`,
      };
    }
    
    const data = await response.json();
    return parseOllamaResponse(data.response);
  } catch (error) {
    console.error('Error processing itinerary with Ollama:', error);
    return {
      success: false,
      message: `Failed to process itinerary: ${error.message}`,
    };
  }
};

/**
 * Create a prompt for Ollama
 * @param {string} text - The itinerary text
 * @returns {string} - Formatted prompt
 */
const createPrompt = (text) => {
  return `
You are a specialized assistant that extracts calendar event information from travel itineraries.
Please analyze the following travel itinerary text and extract the relevant details to create a calendar event.

For FLIGHT itineraries, extract:
- Flight number and airline
- Departure and arrival airports
- Departure and arrival date and time (with time zones if available)
- Passenger name
- Confirmation/booking reference
- Seat information if available

For HOTEL reservations, extract:
- Hotel name
- Check-in and check-out dates and times
- Guest name
- Confirmation number
- Room type if available
- Address of the hotel

For CAR RENTALS, extract:
- Rental company
- Pick-up and drop-off locations
- Pick-up and drop-off dates and times
- Confirmation number
- Vehicle type if available

Format your response as a JSON object with the following structure:

{
  "eventType": "flight|hotel|car_rental|other",
  "summary": "Brief summary of the event",
  "startDateTime": "ISO format date and time (YYYY-MM-DDTHH:MM:SS)",
  "endDateTime": "ISO format date and time (YYYY-MM-DDTHH:MM:SS)",
  "location": "Location of the event",
  "description": "Detailed description including confirmation numbers and other relevant details"
}

For flights, the summary should be in the format "Flight: [Airline] [Flight#] [Origin]-[Destination]"
For hotels, the summary should be in the format "Hotel: [Hotel Name]"
For car rentals, the summary should be in the format "Car Rental: [Company]"

If you cannot determine any field, use null for that field.
Only respond with the JSON object, no additional text.

Here is the itinerary text:

${text}
`;
};

/**
 * Parse the response from Ollama
 * @param {string} response - Raw response from Ollama
 * @returns {Object} - Parsed calendar data
 */
const parseOllamaResponse = (response) => {
  try {
    // Try to extract JSON from the response
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    const jsonStr = jsonMatch ? jsonMatch[0] : response;
    
    // Parse the JSON
    const calendarData = JSON.parse(jsonStr);
    
    // Validate required fields
    if (!calendarData.summary || !calendarData.startDateTime) {
      return {
        success: false,
        message: 'Could not extract required calendar information from the text',
        rawResponse: response,
      };
    }
    
    // Normalize dates to ISO format if needed
    if (calendarData.startDateTime && !isIsoDate(calendarData.startDateTime)) {
      calendarData.startDateTime = new Date(calendarData.startDateTime).toISOString();
    }
    
    if (calendarData.endDateTime && !isIsoDate(calendarData.endDateTime)) {
      calendarData.endDateTime = new Date(calendarData.endDateTime).toISOString();
    }
    
    return {
      success: true,
      calendarData,
    };
  } catch (error) {
    console.error('Error parsing Ollama response:', error);
    return {
      success: false,
      message: 'Failed to parse the response from Ollama',
      rawResponse: response,
    };
  }
};

/**
 * Check if a string is in ISO date format
 * @param {string} str - Date string to check
 * @returns {boolean} - True if string is in ISO format
 */
const isIsoDate = (str) => {
  if (!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(str)) {
    return false;
  }
  try {
    const d = new Date(str);
    return d.toISOString().startsWith(str.split('.')[0]);
  } catch (e) {
    return false;
  }
};
