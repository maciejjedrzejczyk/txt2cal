/**
 * Integration tests for txt2cal
 */

import { processItinerary } from '../services/processingService';
import { sampleItineraries, expectedResults, validateTestResult } from '../utils/testUtils';
import { validateCalendarData } from '../utils/calendarUtils';

// Mock the API services
jest.mock('../services/ollamaService', () => ({
  checkOllamaStatus: jest.fn().mockResolvedValue(true),
  processItinerary: jest.fn().mockImplementation(async (text) => {
    // Simulate successful processing based on the text content
    if (text.includes('FLIGHT CONFIRMATION')) {
      return {
        success: true,
        calendarData: {
          eventType: 'flight',
          summary: 'Flight: AA 123 JFK-SFO',
          startDateTime: '2025-06-15T10:30:00-04:00',
          endDateTime: '2025-06-15T13:45:00-07:00',
          location: 'New York JFK to San Francisco SFO',
          description: 'Confirmation: ABC123\nPassenger: John Doe\nSeat: 15A'
        }
      };
    } else if (text.includes('HOTEL RESERVATION')) {
      return {
        success: true,
        calendarData: {
          eventType: 'hotel',
          summary: 'Hotel: Grand Plaza Hotel',
          startDateTime: '2025-06-15T15:00:00',
          endDateTime: '2025-06-18T11:00:00',
          location: '123 Main Street, San Francisco, CA 94105',
          description: 'Booking Reference: HR789456\nGuest: John Doe\nRoom Type: Deluxe King\nGuests: 2 Adults\nRate: $199.00 per night'
        }
      };
    } else if (text.includes('CAR RENTAL')) {
      return {
        success: true,
        calendarData: {
          eventType: 'car_rental',
          summary: 'Car Rental: Hertz',
          startDateTime: '2025-06-15T14:30:00',
          endDateTime: '2025-06-18T10:00:00',
          location: 'San Francisco International Airport (SFO)',
          description: 'Confirmation: CR456789\nName: John Doe\nVehicle Type: Midsize SUV\nRate: $45.00 per day\nPrepaid: Yes'
        }
      };
    } else if (text.includes('RESTAURANT RESERVATION')) {
      return {
        success: true,
        calendarData: {
          eventType: 'restaurant',
          summary: 'Restaurant: The Fine Dining Experience',
          startDateTime: '2025-06-15T19:30:00',
          endDateTime: '2025-06-15T21:30:00',
          location: '456 Gourmet Ave, San Francisco, CA 94105',
          description: 'Confirmation: RES12345\nName: John Doe\nParty Size: 2\nSpecial Requests: Window table if possible'
        }
      };
    } else if (text.includes('TRAVEL ITINERARY')) {
      return {
        success: true,
        calendarData: {
          eventType: 'flight',
          summary: 'Flight: AA 123 JFK-SFO',
          startDateTime: '2025-06-15T10:30:00-04:00',
          endDateTime: '2025-06-15T13:45:00-07:00',
          location: 'New York JFK to San Francisco SFO',
          description: 'Confirmation: ABC123\nPassenger: John Doe\nSeat: 15A\nClass: Economy'
        }
      };
    } else if (text.includes('incomplete')) {
      return {
        success: false,
        message: 'Could not extract required calendar information from the text'
      };
    } else {
      return {
        success: false,
        message: 'Failed to process itinerary'
      };
    }
  })
}));

jest.mock('../services/apiService', () => ({
  checkServerStatus: jest.fn().mockResolvedValue(false),
  processItinerary: jest.fn()
}));

describe('Integration Tests', () => {
  test('should process flight itinerary correctly', async () => {
    const result = await processItinerary(sampleItineraries.flight);
    expect(result.success).toBe(true);
    expect(result.calendarData).toBeDefined();
    
    const validation = validateTestResult(result.calendarData, expectedResults.flight);
    expect(validation.success).toBe(true);
  });
  
  test('should process hotel reservation correctly', async () => {
    const result = await processItinerary(sampleItineraries.hotel);
    expect(result.success).toBe(true);
    expect(result.calendarData).toBeDefined();
    
    const validation = validateTestResult(result.calendarData, expectedResults.hotel);
    expect(validation.success).toBe(true);
  });
  
  test('should process car rental correctly', async () => {
    const result = await processItinerary(sampleItineraries.carRental);
    expect(result.success).toBe(true);
    expect(result.calendarData).toBeDefined();
    
    const validation = validateTestResult(result.calendarData, expectedResults.carRental);
    expect(validation.success).toBe(true);
  });
  
  test('should process restaurant reservation correctly', async () => {
    const result = await processItinerary(sampleItineraries.restaurant);
    expect(result.success).toBe(true);
    expect(result.calendarData).toBeDefined();
    expect(result.calendarData.eventType).toBe('restaurant');
  });
  
  test('should handle complex itineraries by extracting the first event', async () => {
    const result = await processItinerary(sampleItineraries.complex);
    expect(result.success).toBe(true);
    expect(result.calendarData).toBeDefined();
    expect(result.calendarData.eventType).toBe('flight');
  });
  
  test('should handle incomplete itineraries gracefully', async () => {
    const result = await processItinerary(sampleItineraries.incomplete);
    expect(result.success).toBe(false);
    expect(result.message).toBeDefined();
  });
  
  test('should validate calendar data correctly', () => {
    const validData = {
      summary: 'Test Event',
      startDateTime: '2025-06-15T10:00:00',
      endDateTime: '2025-06-15T11:00:00',
      location: 'Test Location',
      description: 'Test Description'
    };
    
    const invalidData = {
      summary: 'Test Event',
      startDateTime: '2025-06-15T10:00:00',
      endDateTime: '2025-06-14T11:00:00', // End date before start date
      location: 'Test Location'
    };
    
    const validResult = validateCalendarData(validData);
    expect(validResult.isValid).toBe(true);
    
    const invalidResult = validateCalendarData(invalidData);
    expect(invalidResult.isValid).toBe(false);
    expect(invalidResult.errors).toContain('End date/time is before start date/time');
  });
});
