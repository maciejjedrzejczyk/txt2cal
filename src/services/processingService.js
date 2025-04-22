/**
 * Service for processing itinerary text
 * This service decides whether to use local Ollama or the backend API
 */

import * as ollamaService from './ollamaService';
import * as apiService from './apiService';

// Flag to determine if we should use local Ollama or backend API
let useLocalOllama = true;
let ollamaAvailable = false;
let serverAvailable = false;

/**
 * Initialize the processing service by checking available services
 */
export const initProcessingService = async () => {
  try {
    // Check if local Ollama is available
    ollamaAvailable = await ollamaService.checkOllamaStatus();
    
    // Check if backend server is available
    serverAvailable = await apiService.checkServerStatus();
    
    // Decide which service to use
    useLocalOllama = ollamaAvailable;
    
    console.log(`Processing service initialized: Using ${useLocalOllama ? 'local Ollama' : 'backend API'}`);
    
    return {
      ollamaAvailable,
      serverAvailable,
      useLocalOllama
    };
  } catch (error) {
    console.error('Error initializing processing service:', error);
    return {
      ollamaAvailable: false,
      serverAvailable: false,
      useLocalOllama: false
    };
  }
};

/**
 * Process itinerary text using the best available service
 * @param {string} text - The itinerary text to process
 * @returns {Promise<Object>} - Processed calendar data
 */
export const processItinerary = async (text) => {
  // If we haven't initialized yet, do it now
  if (ollamaAvailable === false && serverAvailable === false) {
    await initProcessingService();
  }
  
  // Use local Ollama if available, otherwise use backend API
  if (useLocalOllama) {
    return ollamaService.processItinerary(text);
  } else if (serverAvailable) {
    return apiService.processItinerary(text);
  } else {
    return {
      success: false,
      message: 'No processing service available. Please ensure either Ollama is running locally or the backend server is accessible.'
    };
  }
};

/**
 * Check the status of the processing service
 * @returns {Promise<Object>} - Status object
 */
export const checkStatus = async () => {
  // Check local Ollama status
  const ollamaStatus = await ollamaService.checkOllamaStatus();
  
  // Check backend server status
  const serverStatus = await apiService.checkServerStatus();
  
  // Update our flags
  ollamaAvailable = ollamaStatus;
  serverAvailable = serverStatus;
  useLocalOllama = ollamaAvailable;
  
  return {
    ollamaAvailable,
    serverAvailable,
    useLocalOllama
  };
};
