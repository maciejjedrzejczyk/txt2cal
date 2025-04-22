# txt2cal User Guide

Welcome to txt2cal, a web application that transforms unstructured travel itinerary text into calendar invites using LLM technology.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Using txt2cal](#using-txt2cal)
3. [Supported Itinerary Types](#supported-itinerary-types)
4. [Keyboard Shortcuts](#keyboard-shortcuts)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

## Getting Started

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Either:
  - Ollama installed locally (for local processing)
  - Access to the txt2cal backend server

### Accessing txt2cal

You can access txt2cal in one of two ways:

1. **Web Version**: Visit the hosted version at [https://yourdomain.com/txt2cal](https://yourdomain.com/txt2cal)
2. **Local Installation**: Follow the installation instructions in the README.md file

### Connection Status

When you open txt2cal, you'll see a status indicator in the top-right corner:

- **Green**: Connected to local Ollama
- **Blue**: Using backend server
- **Yellow**: Checking connection
- **Red**: Disconnected (no processing service available)

## Using txt2cal

### Step 1: Input Your Itinerary

1. Paste your travel itinerary text into the input area
   - You can use `Ctrl+V` or `⌘+V` to focus the input area and paste
   - Or click in the text area and paste manually

2. Alternatively, click one of the sample buttons to try a pre-defined itinerary:
   - Flight Sample
   - Hotel Sample
   - Car Rental Sample
   - Restaurant Sample
   - Complex Itinerary

### Step 2: Process the Itinerary

1. Click the "Convert to Calendar" button
2. Wait for the processing to complete (you'll see a loading spinner)

### Step 3: Review and Download

1. Review the calendar event preview that appears
   - Check the event type, summary, dates, and details
   - Click "View on map" to see the location on Google Maps (if available)

2. Click "Download Calendar File (.ics)" to download the calendar file

### Step 4: Import to Your Calendar

1. Open your preferred calendar application (Google Calendar, Apple Calendar, Outlook, etc.)
2. Import the downloaded .ics file
   - In Google Calendar: Click the "+" next to "Other calendars" > "Import"
   - In Apple Calendar: File > Import
   - In Outlook: File > Open & Export > Import/Export > Import an iCalendar (.ics) file

## Supported Itinerary Types

txt2cal can process various types of travel itineraries:

### Flight Itineraries

Information extracted:
- Flight number and airline
- Departure and arrival airports
- Departure and arrival date and time (with time zones if available)
- Passenger name
- Confirmation/booking reference
- Seat information

Example:
```
FLIGHT CONFIRMATION
Confirmation Code: ABC123
PASSENGER: John Doe
FROM: New York JFK
TO: San Francisco SFO
DATE: June 15, 2025
DEPARTURE: 10:30 AM EDT
ARRIVAL: 1:45 PM PDT
FLIGHT: AA 123
SEAT: 15A
```

### Hotel Reservations

Information extracted:
- Hotel name
- Check-in and check-out dates and times
- Guest name
- Confirmation number
- Room type
- Hotel address

Example:
```
HOTEL RESERVATION CONFIRMATION
Booking Reference: HR789456
Guest Name: John Doe
Hotel: Grand Plaza Hotel
Address: 123 Main Street, San Francisco, CA 94105
Check-in: June 15, 2025, 3:00 PM
Check-out: June 18, 2025, 11:00 AM
Room Type: Deluxe King
Guests: 2 Adults
Rate: $199.00 per night
```

### Car Rentals

Information extracted:
- Rental company
- Pick-up and drop-off locations
- Pick-up and drop-off dates and times
- Confirmation number
- Vehicle type

Example:
```
CAR RENTAL CONFIRMATION
Confirmation Number: CR456789
Name: John Doe
Rental Company: Hertz
Pick-up Location: San Francisco International Airport (SFO)
Pick-up Date & Time: June 15, 2025, 2:30 PM
Return Location: San Francisco International Airport (SFO)
Return Date & Time: June 18, 2025, 10:00 AM
Vehicle Type: Midsize SUV
Rate: $45.00 per day
```

### Restaurant Reservations

Information extracted:
- Restaurant name
- Reservation date and time
- Party size
- Confirmation number
- Restaurant address

Example:
```
RESTAURANT RESERVATION
Confirmation #: RES12345
Name: John Doe
Restaurant: The Fine Dining Experience
Date: June 15, 2025
Time: 7:30 PM
Party Size: 2
Address: 456 Gourmet Ave, San Francisco, CA 94105
```

## Keyboard Shortcuts

- `Ctrl+V` or `⌘+V`: Focus the text input area and paste from clipboard
- `Escape`: Dismiss error messages

## Troubleshooting

### Common Issues

#### "No processing service available"

- **Cause**: Neither local Ollama nor the backend server is accessible
- **Solution**: 
  - Ensure Ollama is installed and running locally
  - Check your internet connection if using the backend server

#### "Could not extract required calendar information"

- **Cause**: The itinerary format couldn't be properly parsed
- **Solution**:
  - Try using one of the sample itineraries to see the expected format
  - Make sure your itinerary includes dates, times, and key details
  - Try reformatting the text to make it clearer

#### "Failed to process itinerary"

- **Cause**: An error occurred during processing
- **Solution**:
  - Try again with a simpler itinerary
  - Check if Ollama is running properly
  - Try using the backend server instead

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/yourusername/txt2cal/issues) for similar problems
2. Report a new issue with details about your problem
3. Include the itinerary text (with personal information removed) and error messages

## FAQ

### Q: Is my data private?

**A**: Yes. When using local Ollama processing, all your data stays on your computer. If using the backend server, data is processed securely and not stored permanently.

### Q: What calendar apps can I use with the .ics files?

**A**: The generated .ics files are compatible with most calendar applications, including:
- Google Calendar
- Apple Calendar
- Microsoft Outlook
- Mozilla Thunderbird
- Most smartphone calendar apps

### Q: Can I process multiple events at once?

**A**: Currently, txt2cal processes one event at a time. For complex itineraries with multiple events, you'll need to process each section separately.

### Q: Does txt2cal work offline?

**A**: Yes, if you're using local Ollama processing. If you're using the backend server, you'll need an internet connection.

### Q: How accurate is the information extraction?

**A**: txt2cal uses advanced LLM technology to extract information, but accuracy depends on the clarity and format of the input text. Always review the calendar preview before downloading.
