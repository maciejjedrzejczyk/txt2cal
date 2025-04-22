import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import Footer from './components/Footer';
import ItineraryInput from './components/ItineraryInput';
import CalendarPreview from './components/CalendarPreview';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import { processItinerary, initProcessingService } from './services/processingService';
import { generateICSFile, downloadICSFile, validateCalendarData, generateFilename } from './utils/calendarUtils';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [serviceInitialized, setServiceInitialized] = useState(false);

  // Initialize the processing service
  useEffect(() => {
    const initService = async () => {
      await initProcessingService();
      setServiceInitialized(true);
    };
    
    initService();
  }, []);

  const handleSubmit = async (text) => {
    setIsProcessing(true);
    setResult(null);
    setError(null);

    try {
      const response = await processItinerary(text);
      
      if (response.success) {
        // Validate the calendar data
        const validation = validateCalendarData(response.calendarData);
        
        if (validation.isValid) {
          setResult(response.calendarData);
        } else {
          setError(`Invalid calendar data: ${validation.errors.join(', ')}`);
        }
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError(`An error occurred: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (result) {
      const icsContent = generateICSFile(result);
      const filename = generateFilename(result);
      downloadICSFile(icsContent, filename);
    }
  };

  const dismissError = () => {
    setError(null);
  };

  return (
    <div className="App">
      <Header />
      
      <main className="App-main">
        <ItineraryInput onSubmit={handleSubmit} isProcessing={isProcessing} />
        
        {isProcessing && <LoadingSpinner />}
        
        {error && <ErrorMessage message={error} onDismiss={dismissError} />}
        
        {result && <CalendarPreview calendarData={result} onDownload={handleDownload} />}
      </main>
      
      <Footer />
    </div>
  );
}

export default App;
