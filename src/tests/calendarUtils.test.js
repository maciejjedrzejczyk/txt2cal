/**
 * Tests for calendar utility functions
 */

import { 
  generateICSFile, 
  generateFilename, 
  validateCalendarData,
  getEventTypeName
} from '../utils/calendarUtils';

// Mock Date.now() to return a consistent value for testing
const originalDateNow = Date.now;
beforeAll(() => {
  global.Date.now = jest.fn(() => 1625097600000); // 2021-07-01T00:00:00.000Z
});

afterAll(() => {
  global.Date.now = originalDateNow;
});

describe('Calendar Utilities', () => {
  describe('generateICSFile', () => {
    test('should generate a valid ICS file', () => {
      const calendarData = {
        eventType: 'flight',
        summary: 'Flight: AA 123 JFK-SFO',
        startDateTime: '2025-06-15T10:30:00-04:00',
        endDateTime: '2025-06-15T13:45:00-07:00',
        location: 'New York JFK to San Francisco SFO',
        description: 'Confirmation: ABC123\nPassenger: John Doe\nSeat: 15A'
      };
      
      const icsContent = generateICSFile(calendarData);
      
      // Check that the ICS file contains the required fields
      expect(icsContent).toContain('BEGIN:VCALENDAR');
      expect(icsContent).toContain('VERSION:2.0');
      expect(icsContent).toContain('BEGIN:VEVENT');
      expect(icsContent).toContain('SUMMARY:Flight: AA 123 JFK-SFO');
      expect(icsContent).toContain('DTSTART:');
      expect(icsContent).toContain('DTEND:');
      expect(icsContent).toContain('LOCATION:New York JFK to San Francisco SFO');
      expect(icsContent).toContain('DESCRIPTION:Confirmation: ABC123\\nPassenger: John Doe\\nSeat: 15A');
      expect(icsContent).toContain('END:VEVENT');
      expect(icsContent).toContain('END:VCALENDAR');
    });
    
    test('should handle missing optional fields', () => {
      const calendarData = {
        eventType: 'other',
        summary: 'Test Event',
        startDateTime: '2025-06-15T10:30:00',
        endDateTime: '2025-06-15T11:30:00'
      };
      
      const icsContent = generateICSFile(calendarData);
      
      // Check that the ICS file contains the required fields
      expect(icsContent).toContain('BEGIN:VCALENDAR');
      expect(icsContent).toContain('SUMMARY:Test Event');
      expect(icsContent).toContain('DTSTART:');
      expect(icsContent).toContain('DTEND:');
      
      // Check that optional fields are not included
      expect(icsContent).not.toContain('LOCATION:');
      expect(icsContent).not.toContain('DESCRIPTION:');
      
      expect(icsContent).toContain('END:VCALENDAR');
    });
  });
  
  describe('generateFilename', () => {
    test('should generate a valid filename for flight events', () => {
      const calendarData = {
        eventType: 'flight',
        summary: 'Flight: AA 123 JFK-SFO',
        startDateTime: '2025-06-15T10:30:00'
      };
      
      const filename = generateFilename(calendarData);
      expect(filename).toBe('flight_2025-06-15_Flight_AA_123_JFK_SFO.ics');
    });
    
    test('should generate a valid filename for hotel events', () => {
      const calendarData = {
        eventType: 'hotel',
        summary: 'Hotel: Grand Plaza Hotel',
        startDateTime: '2025-06-15T15:00:00'
      };
      
      const filename = generateFilename(calendarData);
      expect(filename).toBe('hotel_2025-06-15_Hotel_Grand_Plaza_Hotel.ics');
    });
    
    test('should handle missing event type', () => {
      const calendarData = {
        summary: 'Test Event',
        startDateTime: '2025-06-15T10:30:00'
      };
      
      const filename = generateFilename(calendarData);
      expect(filename).toBe('event_2025-06-15_Test_Event.ics');
    });
  });
  
  describe('validateCalendarData', () => {
    test('should validate valid calendar data', () => {
      const calendarData = {
        summary: 'Test Event',
        startDateTime: '2025-06-15T10:00:00',
        endDateTime: '2025-06-15T11:00:00'
      };
      
      const result = validateCalendarData(calendarData);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
    
    test('should reject calendar data with missing summary', () => {
      const calendarData = {
        startDateTime: '2025-06-15T10:00:00',
        endDateTime: '2025-06-15T11:00:00'
      };
      
      const result = validateCalendarData(calendarData);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Missing event summary');
    });
    
    test('should reject calendar data with missing start date', () => {
      const calendarData = {
        summary: 'Test Event',
        endDateTime: '2025-06-15T11:00:00'
      };
      
      const result = validateCalendarData(calendarData);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Missing start date/time');
    });
    
    test('should reject calendar data with invalid date format', () => {
      const calendarData = {
        summary: 'Test Event',
        startDateTime: 'invalid date',
        endDateTime: '2025-06-15T11:00:00'
      };
      
      const result = validateCalendarData(calendarData);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Invalid start date/time format');
    });
    
    test('should reject calendar data with end date before start date', () => {
      const calendarData = {
        summary: 'Test Event',
        startDateTime: '2025-06-15T10:00:00',
        endDateTime: '2025-06-14T11:00:00'
      };
      
      const result = validateCalendarData(calendarData);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('End date/time is before start date/time');
    });
  });
  
  describe('getEventTypeName', () => {
    test('should return correct name for flight events', () => {
      expect(getEventTypeName('flight')).toBe('Flight');
    });
    
    test('should return correct name for hotel events', () => {
      expect(getEventTypeName('hotel')).toBe('Hotel');
    });
    
    test('should return correct name for car rental events', () => {
      expect(getEventTypeName('car_rental')).toBe('Car Rental');
    });
    
    test('should return correct name for restaurant events', () => {
      expect(getEventTypeName('restaurant')).toBe('Restaurant');
    });
    
    test('should return default name for unknown event types', () => {
      expect(getEventTypeName('unknown')).toBe('Event');
      expect(getEventTypeName('')).toBe('Event');
      expect(getEventTypeName(undefined)).toBe('Event');
    });
  });
});
