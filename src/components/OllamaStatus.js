import React, { useState, useEffect } from 'react';
import { checkStatus } from '../services/processingService';

/**
 * Component to display processing service status
 */
function OllamaStatus() {
  const [status, setStatus] = useState('checking');
  const [statusDetails, setStatusDetails] = useState({
    ollamaAvailable: false,
    serverAvailable: false,
    useLocalOllama: false
  });

  useEffect(() => {
    const checkServiceStatus = async () => {
      setStatus('checking');
      try {
        const result = await checkStatus();
        setStatusDetails(result);
        
        if (result.ollamaAvailable) {
          setStatus('connected');
        } else if (result.serverAvailable) {
          setStatus('server');
        } else {
          setStatus('disconnected');
        }
      } catch (error) {
        console.error('Error checking status:', error);
        setStatus('disconnected');
      }
    };

    checkServiceStatus();
    
    // Check status periodically
    const interval = setInterval(checkServiceStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusText = () => {
    switch (status) {
      case 'checking':
        return 'Checking connection...';
      case 'connected':
        return 'Ollama: Connected';
      case 'server':
        return 'Using Server API';
      case 'disconnected':
        return 'Disconnected - Please ensure Ollama or server is running';
      default:
        return 'Unknown status';
    }
  };

  return (
    <div className={`ollama-status ${status}`}>
      <span className="status-indicator"></span>
      <span className="status-text">
        {getStatusText()}
      </span>
    </div>
  );
}

export default OllamaStatus;
