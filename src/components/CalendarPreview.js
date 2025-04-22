import React from 'react';
import { getEventTypeName } from '../utils/calendarUtils';

/**
 * Component for previewing calendar event before download
 */
function CalendarPreview({ calendarData, onDownload }) {
  if (!calendarData) return null;
  
  const {
    eventType,
    summary,
    startDateTime,
    endDateTime,
    location,
    description
  } = calendarData;
  
  // Format dates for display
  const formatDate = (dateString) => {
    if (!dateString) return 'Not specified';
    
    const options = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      timeZoneName: 'short'
    };
    
    try {
      return new Date(dateString).toLocaleString(undefined, options);
    } catch (e) {
      return dateString;
    }
  };
  
  // Format description for display
  const formatDescription = (desc) => {
    if (!desc) return null;
    return desc.split('\n').map((line, i) => (
      <div key={i} className="description-line">{line}</div>
    ));
  };
  
  // Get event type icon
  const getEventIcon = () => {
    switch (eventType) {
      case 'flight':
        return '✈️';
      case 'hotel':
        return '🏨';
      case 'car_rental':
        return '🚗';
      case 'restaurant':
        return '🍽️';
      case 'meeting':
        return '📅';
      default:
        return '📆';
    }
  };
  
  // Get map link if location is available
  const getMapLink = () => {
    if (!location) return null;
    
    const encodedLocation = encodeURIComponent(location);
    return (
      <a 
        href={`https://maps.google.com/?q=${encodedLocation}`}
        target="_blank"
        rel="noopener noreferrer"
        className="map-link"
        title="View on map"
      >
        View on map 🗺️
      </a>
    );
  };
  
  return (
    <div className="calendar-preview">
      <h2>Calendar Event Preview</h2>
      
      <div className="preview-content">
        <div className="event-header">
          <span className="event-icon">{getEventIcon()}</span>
          <span className="event-type">{getEventTypeName(eventType)}</span>
        </div>
        
        <div className="event-summary">
          <h3>{summary}</h3>
        </div>
        
        <div className="event-details">
          <div className="detail-row">
            <span className="detail-label">Start:</span>
            <span className="detail-value">{formatDate(startDateTime)}</span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">End:</span>
            <span className="detail-value">{formatDate(endDateTime)}</span>
          </div>
          
          {location && (
            <div className="detail-row">
              <span className="detail-label">Location:</span>
              <span className="detail-value">
                {location}
                {getMapLink()}
              </span>
            </div>
          )}
          
          {description && (
            <div className="detail-row description">
              <span className="detail-label">Details:</span>
              <div className="detail-value description-value">
                {formatDescription(description)}
              </div>
            </div>
          )}
        </div>
        
        <div className="download-container">
          <button 
            className="download-button"
            onClick={onDownload}
          >
            Download Calendar File (.ics)
          </button>
          <div className="download-hint">
            Import this file into Google Calendar, Apple Calendar, Outlook, or any other calendar app
          </div>
        </div>
      </div>
    </div>
  );
}

export default CalendarPreview;
