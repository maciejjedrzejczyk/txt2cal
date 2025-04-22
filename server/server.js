/**
 * txt2cal Backend Server
 */

// Load environment variables from .env file
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');

// Create Express app
const app = express();

// Configuration
const PORT = process.env.PORT || 3001;
const OLLAMA_API_URL = process.env.OLLAMA_API_URL || 'http://localhost:11434/api';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'llama3.2';
const CORS_ORIGINS = process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ['http://localhost:3000'];
const RATE_LIMIT = process.env.RATE_LIMIT || 100;

// Log configuration
console.log('Server configuration:');
console.log(`- Port: ${PORT}`);
console.log(`- Ollama API URL: ${OLLAMA_API_URL}`);
console.log(`- Ollama Model: ${OLLAMA_MODEL}`);
console.log(`- CORS Origins: ${CORS_ORIGINS.join(', ')}`);
console.log(`- Rate Limit: ${RATE_LIMIT} requests per 15 minutes`);

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir);
}

// Create a write stream for access logs
const accessLogStream = fs.createWriteStream(
  path.join(logsDir, 'access.log'),
  { flags: 'a' }
);

// Middleware
app.use(cors({
  origin: CORS_ORIGINS,
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json({ limit: '1mb' }));
app.use(morgan('combined', { stream: accessLogStream }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: RATE_LIMIT, // limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    status: 429,
    message: 'Too many requests, please try again later.'
  }
});

// Apply rate limiting to all routes
app.use(limiter);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString()
  });
});

// Ollama status endpoint
app.get('/api/ollama/status', async (req, res) => {
  try {
    const response = await fetch(`${OLLAMA_API_URL}/tags`);
    
    if (response.ok) {
      const data = await response.json();
      res.json({
        status: 'connected',
        models: data.models ? data.models.map(model => model.name) : []
      });
    } else {
      res.json({
        status: 'disconnected'
      });
    }
  } catch (error) {
    console.error('Error checking Ollama status:', error);
    res.json({
      status: 'disconnected'
    });
  }
});

// Process itinerary endpoint
app.post('/api/process', async (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text || text.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'No text provided'
      });
    }
    
    // Create prompt for Ollama
    const prompt = createPrompt(text);
    
    // Call Ollama API
    const response = await fetch(`${OLLAMA_API_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: OLLAMA_MODEL,
        prompt,
        stream: false,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Ollama API error:', errorData);
      return res.status(500).json({
        success: false,
        message: `Ollama API error: ${errorData.error || 'Unknown error'}`
      });
    }
    
    const data = await response.json();
    const result = parseOllamaResponse(data.response);
    
    res.json(result);
  } catch (error) {
    console.error('Error processing itinerary:', error);
    res.status(500).json({
      success: false,
      message: `Failed to process itinerary: ${error.message}`
    });
  }
});

// Create a prompt for Ollama
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

// Parse the response from Ollama
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
    console.error('Error parsing Ollama response:', error);
    return {
      success: false,
      message: 'Failed to parse the response from Ollama',
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

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
