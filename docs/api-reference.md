# txt2cal API Reference

This document provides detailed information about the txt2cal API endpoints, request formats, and response structures.

## Base URL

The base URL for all API endpoints is:

```
http://localhost:3001/api
```

For production deployments, replace with your actual domain.

## Authentication

Currently, the API does not require authentication. Rate limiting is applied to prevent abuse.

## Endpoints

### Health Check

Check if the API server is running.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "ok",
  "timestamp": "2025-04-22T13:23:34.000Z"
}
```

### Ollama Status

Check if Ollama is available and which models are installed.

**Endpoint:** `GET /ollama/status`

**Response (Connected):**

```json
{
  "status": "connected",
  "models": ["llama3.2", "mistral", "codellama"]
}
```

**Response (Disconnected):**

```json
{
  "status": "disconnected"
}
```

### Process Itinerary

Process itinerary text and extract calendar event information.

**Endpoint:** `POST /process`

**Request:**

```json
{
  "text": "FLIGHT CONFIRMATION\nConfirmation Code: ABC123\nPASSENGER: John Doe\nFROM: New York JFK\nTO: San Francisco SFO\nDATE: June 15, 2025\nDEPARTURE: 10:30 AM EDT\nARRIVAL: 1:45 PM PDT\nFLIGHT: AA 123\nSEAT: 15A"
}
```

**Response (Success):**

```json
{
  "success": true,
  "calendarData": {
    "eventType": "flight",
    "summary": "Flight: AA 123 JFK-SFO",
    "startDateTime": "2025-06-15T10:30:00-04:00",
    "endDateTime": "2025-06-15T13:45:00-07:00",
    "location": "New York JFK to San Francisco SFO",
    "description": "Confirmation: ABC123\nPassenger: John Doe\nSeat: 15A"
  }
}
```

**Response (Error):**

```json
{
  "success": false,
  "message": "Could not extract required calendar information from the text"
}
```

## Error Codes

The API uses standard HTTP status codes:

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid request parameters
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: Ollama service unavailable

## Rate Limiting

The API is rate-limited to 100 requests per 15-minute window per IP address. When the rate limit is exceeded, the API will respond with a 429 status code.

## Data Structures

### Calendar Data Object

The `calendarData` object returned by the `/process` endpoint has the following structure:

| Field | Type | Description |
|-------|------|-------------|
| `eventType` | string | Type of event: `flight`, `hotel`, `car_rental`, `restaurant`, or `other` |
| `summary` | string | Brief summary of the event |
| `startDateTime` | string | Start date and time in ISO format |
| `endDateTime` | string | End date and time in ISO format |
| `location` | string | Location of the event |
| `description` | string | Detailed description with confirmation numbers and other details |

## Client Integration

### JavaScript Example

```javascript
async function processItinerary(text) {
  try {
    const response = await fetch('http://localhost:3001/api/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Unknown error');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error processing itinerary:', error);
    return {
      success: false,
      message: `Failed to process itinerary: ${error.message}`,
    };
  }
}
```

### cURL Example

```bash
curl -X POST \
  http://localhost:3001/api/process \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "FLIGHT CONFIRMATION\nConfirmation Code: ABC123\nPASSENGER: John Doe\nFROM: New York JFK\nTO: San Francisco SFO\nDATE: June 15, 2025\nDEPARTURE: 10:30 AM EDT\nARRIVAL: 1:45 PM PDT\nFLIGHT: AA 123\nSEAT: 15A"
  }'
```

## Error Handling

The API provides detailed error messages to help diagnose issues. Common errors include:

- Invalid input text (empty or too long)
- Ollama connection issues
- Parsing failures when extracting calendar information

Always check the `success` field in the response to determine if the request was successful.

## Versioning

The current API version is v1. The version is implicit in the current implementation.

Future versions will be explicitly versioned in the URL path (e.g., `/api/v2/process`).

## Support

For API support or to report issues, please open an issue on the [GitHub repository](https://github.com/yourusername/txt2cal/issues).
