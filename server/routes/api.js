/**
 * API routes
 */

const express = require('express');
const { body, validationResult } = require('express-validator');
const fetch = require('node-fetch');
const router = express.Router();

// Configuration
const OLLAMA_API_URL = process.env.OLLAMA_API_URL || 'http://localhost:11434/api';
const MODEL = process.env.OLLAMA_MODEL || 'llama3.2';

// Health check endpoint
router.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Ollama status endpoint
router.get('/ollama/status', async (req, res) => {
  try {
    const response = await fetch(`${OLLAMA_API_URL}/tags`);
    if (!response.ok) {
      return res.status(503).json({ status: 'disconnected' });
    }
    const data = await response.json();
    return res.status(200).json({ 
      status: 'connected',
      models: data.models.map(model => model.name)
    });
  } catch (error) {
    console.error('Error checking Ollama status:', error);
    return res.status(503).json({ status: 'disconnected', error: error.message });
  }
});

// Process itinerary endpoint
router.post(
  '/process',
  [
    body('text').notEmpty().withMessage('Itinerary text is required'),
    body('text').isLength({ max: 10000 }).withMessage('Text too long (max 10000 characters)')
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { text } = req.body;

    try {
      // Create prompt for Ollama
      const prompt = createPrompt(text);

      // Call Ollama API
      const ollamaResponse = await fetch(`${OLLAMA_API_URL}/generate`, {
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

      if (!ollamaResponse.ok) {
        const errorData = await ollamaResponse.json();
        console.error('Ollama API error:', errorData);
        return res.status(500).json({ 
          success: false, 
          message: `Ollama API error: ${errorData.error || 'Unknown error'}` 
        });
      }

      const data = await ollamaResponse.json();
      const parsedResponse = parseOllamaResponse(data.response);
      
      return res.status(200).json(parsedResponse);
    } catch (error) {
      console.error('Error processing itinerary:', error);
      return res.status(500).json({ 
        success: false, 
        message: `Failed to process itinerary: ${error.message}` 
      });
    }
  }
);

// Create prompt for Ollama
function createPrompt(text) {
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
}

// Parse Ollama response
function parseOllamaResponse(response) {
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
    console.error('Error parsing LLM response:', error);
    return {
      success: false,
      message: 'Failed to parse the response from the LLM',
      rawResponse: response,
    };
  }
}

// Check if a string is in ISO date format
function isIsoDate(str) {
  if (!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(str)) {
    return false;
  }
  try {
    const d = new Date(str);
    return d.toISOString().startsWith(str.split('.')[0]);
  } catch (e) {
    return false;
  }
}

module.exports = router;
