/**
 * Utility functions for testing
 */

/**
 * Sample itineraries for testing
 */
export const sampleItineraries = {
  flight: `FLIGHT CONFIRMATION
Confirmation Code: ABC123
PASSENGER: John Doe
FROM: New York JFK
TO: San Francisco SFO
DATE: June 15, 2025
DEPARTURE: 10:30 AM EDT
ARRIVAL: 1:45 PM PDT
FLIGHT: AA 123
SEAT: 15A`,

  hotel: `HOTEL RESERVATION CONFIRMATION
Booking Reference: HR789456
Guest Name: John Doe
Hotel: Grand Plaza Hotel
Address: 123 Main Street, San Francisco, CA 94105
Check-in: June 15, 2025, 3:00 PM
Check-out: June 18, 2025, 11:00 AM
Room Type: Deluxe King
Guests: 2 Adults
Rate: $199.00 per night
Reservation made through: Hotels.com`,

  carRental: `CAR RENTAL CONFIRMATION
Confirmation Number: CR456789
Name: John Doe
Rental Company: Hertz
Pick-up Location: San Francisco International Airport (SFO)
Pick-up Date & Time: June 15, 2025, 2:30 PM
Return Location: San Francisco International Airport (SFO)
Return Date & Time: June 18, 2025, 10:00 AM
Vehicle Type: Midsize SUV
Rate: $45.00 per day
Prepaid: Yes`,

  restaurant: `RESTAURANT RESERVATION
Confirmation #: RES12345
Name: John Doe
Restaurant: The Fine Dining Experience
Date: June 15, 2025
Time: 7:30 PM
Party Size: 2
Special Requests: Window table if possible
Address: 456 Gourmet Ave, San Francisco, CA 94105
Phone: (555) 123-4567`,

  complex: `TRAVEL ITINERARY - BOOKING #TRP987654

PASSENGER: John Doe
EMAIL: john.doe@example.com
PHONE: (555) 987-6543

FLIGHT DETAILS:
Outbound: June 15, 2025
American Airlines Flight AA 123
From: New York (JFK) - Departs: 10:30 AM EDT
To: San Francisco (SFO) - Arrives: 1:45 PM PDT
Confirmation: ABC123
Seat: 15A
Class: Economy

Return: June 18, 2025
United Airlines Flight UA 456
From: San Francisco (SFO) - Departs: 3:20 PM PDT
To: New York (JFK) - Arrives: 11:55 PM EDT
Confirmation: DEF456
Seat: 22C
Class: Economy

HOTEL DETAILS:
Grand Plaza Hotel
123 Main Street, San Francisco, CA 94105
Check-in: June 15, 2025, 3:00 PM
Check-out: June 18, 2025, 11:00 AM
Room Type: Deluxe King
Guests: 1 Adult
Rate: $199.00 per night
Booking Reference: HR789456

CAR RENTAL:
Hertz
Pick-up: San Francisco International Airport (SFO)
Date: June 15, 2025, 2:30 PM
Return: San Francisco International Airport (SFO)
Date: June 18, 2025, 10:00 AM
Vehicle: Midsize SUV
Confirmation: CR456789

RESTAURANT RESERVATION:
The Fine Dining Experience
Date: June 15, 2025
Time: 7:30 PM
Party Size: 1
Confirmation: RES12345
Address: 456 Gourmet Ave, San Francisco, CA 94105`,

  incomplete: `FLIGHT INFO
From: New York
To: San Francisco
Passenger: John Doe`,

  malformatted: `FLT: AA123 15JUN JFK-SFO 1030A 145P
PASSENGER: DOE/JOHN
REF: ABC123
SEAT: 15A`
};

/**
 * Expected results for sample itineraries
 */
export const expectedResults = {
  flight: {
    eventType: 'flight',
    summary: 'Flight: AA 123 JFK-SFO',
    startDateTime: '2025-06-15T10:30:00-04:00',
    endDateTime: '2025-06-15T13:45:00-07:00',
    location: 'New York JFK to San Francisco SFO',
    description: 'Confirmation: ABC123\nPassenger: John Doe\nSeat: 15A'
  },
  
  hotel: {
    eventType: 'hotel',
    summary: 'Hotel: Grand Plaza Hotel',
    startDateTime: '2025-06-15T15:00:00',
    endDateTime: '2025-06-18T11:00:00',
    location: '123 Main Street, San Francisco, CA 94105',
    description: 'Booking Reference: HR789456\nGuest: John Doe\nRoom Type: Deluxe King\nGuests: 2 Adults\nRate: $199.00 per night'
  },
  
  carRental: {
    eventType: 'car_rental',
    summary: 'Car Rental: Hertz',
    startDateTime: '2025-06-15T14:30:00',
    endDateTime: '2025-06-18T10:00:00',
    location: 'San Francisco International Airport (SFO)',
    description: 'Confirmation: CR456789\nName: John Doe\nVehicle Type: Midsize SUV\nRate: $45.00 per day\nPrepaid: Yes'
  }
};

/**
 * Validate calendar data against expected results
 * @param {Object} actual - Actual calendar data
 * @param {Object} expected - Expected calendar data
 * @returns {Object} - Validation result with success flag and errors
 */
export const validateTestResult = (actual, expected) => {
  const errors = [];
  
  // Check event type
  if (actual.eventType !== expected.eventType) {
    errors.push(`Event type mismatch: expected "${expected.eventType}", got "${actual.eventType}"`);
  }
  
  // Check summary
  if (actual.summary !== expected.summary) {
    errors.push(`Summary mismatch: expected "${expected.summary}", got "${actual.summary}"`);
  }
  
  // Check if dates exist
  if (!actual.startDateTime) {
    errors.push('Missing start date/time');
  }
  
  if (!actual.endDateTime) {
    errors.push('Missing end date/time');
  }
  
  // Check if location exists when expected
  if (expected.location && !actual.location) {
    errors.push('Missing location');
  }
  
  // Check if description exists when expected
  if (expected.description && !actual.description) {
    errors.push('Missing description');
  }
  
  return {
    success: errors.length === 0,
    errors
  };
};
