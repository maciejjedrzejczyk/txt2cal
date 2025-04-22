import React, { useState, useRef, useEffect } from 'react';
import SampleButton from './SampleButton';
import { sampleItineraries } from '../utils/testUtils';

/**
 * Component for itinerary text input
 */
function ItineraryInput({ onSubmit, isProcessing }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);
  
  // Focus the textarea when the component mounts
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);
  
  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl+V or Cmd+V to focus the textarea
      if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
        if (document.activeElement !== textareaRef.current) {
          e.preventDefault();
          textareaRef.current.focus();
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  const handleTextChange = (e) => {
    setText(e.target.value);
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !isProcessing) {
      onSubmit(text);
    }
  };
  
  const handleSampleSelect = (sampleText) => {
    setText(sampleText);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };
  
  const handleClear = () => {
    setText('');
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };
  
  return (
    <div className="itinerary-input-container">
      <form onSubmit={handleSubmit}>
        <div className="textarea-container">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={handleTextChange}
            placeholder="Paste your travel itinerary text here (flight confirmation, hotel reservation, car rental, etc.)"
            disabled={isProcessing}
            rows={10}
            aria-label="Itinerary text input"
          />
          
          {text && (
            <button 
              type="button" 
              className="clear-button" 
              onClick={handleClear}
              title="Clear text"
              aria-label="Clear text"
            >
              ×
            </button>
          )}
        </div>
        
        <div className="sample-buttons">
          <span className="sample-label">Try a sample:</span>
          <SampleButton type="flight" onSelect={handleSampleSelect} />
          <SampleButton type="hotel" onSelect={handleSampleSelect} />
          <SampleButton type="carRental" onSelect={handleSampleSelect} />
          <SampleButton type="restaurant" onSelect={handleSampleSelect} />
          <SampleButton type="complex" onSelect={handleSampleSelect} />
        </div>
        
        <div className="submit-container">
          <button 
            type="submit" 
            className="submit-button"
            disabled={!text.trim() || isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Convert to Calendar'}
          </button>
          
          <div className="keyboard-shortcut-hint">
            <span>Tip: Use Ctrl+V or ⌘+V to quickly focus and paste</span>
          </div>
        </div>
      </form>
    </div>
  );
}

export default ItineraryInput;
