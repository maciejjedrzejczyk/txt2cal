/**
 * Utility functions for calendar operations
 */

/**
 * Generate an ICS file from calendar data
 * @param {Object} calendarData - Calendar event data
 * @returns {string} - ICS file content
 */
export const generateICSFile = (calendarData) => {
  // Generate a unique ID for the event
  const eventUid = generateEventUid();
  
  // Format dates for ICS
  const startDate = formatDateForICS(calendarData.startDateTime);
  const endDate = formatDateForICS(calendarData.endDateTime);
  
  // Create ICS content
  const icsContent = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//txt2cal//EN',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'BEGIN:VEVENT',
    `UID:${eventUid}`,
    `SUMMARY:${calendarData.summary}`,
    `DTSTART:${startDate}`,
    `DTEND:${endDate}`,
    `DTSTAMP:${formatDateForICS(new Date().toISOString())}`,
    `CATEGORIES:${getEventTypeName(calendarData.eventType)}`,
    calendarData.location ? `LOCATION:${calendarData.location}` : '',
    calendarData.description ? `DESCRIPTION:${formatDescriptionForICS(calendarData.description)}` : '',
    'END:VEVENT',
    'END:VCALENDAR'
  ].filter(Boolean).join('\r\n');
  
  return icsContent;
};

/**
 * Download an ICS file
 * @param {string} icsContent - ICS file content
 * @param {string} filename - Filename for the download
 */
export const downloadICSFile = (icsContent, filename) => {
  const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Generate a filename for the calendar file
 * @param {Object} calendarData - Calendar event data
 * @returns {string} - Filename
 */
export const generateFilename = (calendarData) => {
  const eventType = calendarData.eventType || 'event';
  const date = new Date(calendarData.startDateTime).toISOString().split('T')[0];
  const summary = calendarData.summary
    .replace(/[^a-zA-Z0-9]/g, '_')
    .replace(/_+/g, '_')
    .substring(0, 30);
  
  return `${eventType}_${date}_${summary}.ics`;
};

/**
 * Format a date for ICS format
 * @param {string} dateString - ISO date string
 * @returns {string} - Date in ICS format
 */
const formatDateForICS = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  // Format: YYYYMMDDTHHMMSSZ
  return date.toISOString()
    .replace(/[-:]/g, '')
    .replace(/\.\d{3}/g, '');
};

/**
 * Format description text for ICS
 * @param {string} description - Description text
 * @returns {string} - Formatted description
 */
const formatDescriptionForICS = (description) => {
  return description
    .replace(/\n/g, '\\n')
    .replace(/,/g, '\\,')
    .replace(/;/g, '\\;');
};

/**
 * Generate a unique ID for an event
 * @returns {string} - Unique ID
 */
const generateEventUid = () => {
  return `${Date.now()}-${Math.floor(Math.random() * 1000000)}@txt2cal`;
};

/**
 * Get a human-readable name for an event type
 * @param {string} eventType - Event type code
 * @returns {string} - Human-readable event type
 */
export const getEventTypeName = (eventType) => {
  switch (eventType) {
    case 'flight':
      return 'Flight';
    case 'hotel':
      return 'Hotel';
    case 'car_rental':
      return 'Car Rental';
    case 'restaurant':
      return 'Restaurant';
    case 'meeting':
      return 'Meeting';
    default:
      return 'Event';
  }
};

/**
 * Validate calendar data
 * @param {Object} calendarData - Calendar event data
 * @returns {Object} - Validation result with success flag and errors
 */
export const validateCalendarData = (calendarData) => {
  const errors = [];
  
  // Check required fields
  if (!calendarData.summary) {
    errors.push('Missing event summary');
  }
  
  if (!calendarData.startDateTime) {
    errors.push('Missing start date/time');
  } else {
    // Validate start date format
    try {
      new Date(calendarData.startDateTime);
    } catch (e) {
      errors.push('Invalid start date/time format');
    }
  }
  
  if (!calendarData.endDateTime) {
    errors.push('Missing end date/time');
  } else {
    // Validate end date format
    try {
      new Date(calendarData.endDateTime);
    } catch (e) {
      errors.push('Invalid end date/time format');
    }
  }
  
  // Check if end date is after start date
  if (calendarData.startDateTime && calendarData.endDateTime) {
    const start = new Date(calendarData.startDateTime);
    const end = new Date(calendarData.endDateTime);
    
    if (end < start) {
      errors.push('End date/time is before start date/time');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};
