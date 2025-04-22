/**
 * Tests for processing service
 */

import { 
  initProcessingService, 
  processItinerary, 
  checkStatus 
} from '../services/processingService';

// Mock the API services
jest.mock('../services/ollamaService', () => ({
  checkOllamaStatus: jest.fn(),
  processItinerary: jest.fn()
}));

jest.mock('../services/apiService', () => ({
  checkServerStatus: jest.fn(),
  processItinerary: jest.fn()
}));

// Import mocked services
import * as ollamaService from '../services/ollamaService';
import * as apiService from '../services/apiService';

describe('Processing Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('initProcessingService', () => {
    test('should use local Ollama when available', async () => {
      ollamaService.checkOllamaStatus.mockResolvedValue(true);
      apiService.checkServerStatus.mockResolvedValue(true);
      
      const result = await initProcessingService();
      
      expect(result.ollamaAvailable).toBe(true);
      expect(result.serverAvailable).toBe(true);
      expect(result.useLocalOllama).toBe(true);
    });
    
    test('should use backend API when Ollama is not available', async () => {
      ollamaService.checkOllamaStatus.mockResolvedValue(false);
      apiService.checkServerStatus.mockResolvedValue(true);
      
      const result = await initProcessingService();
      
      expect(result.ollamaAvailable).toBe(false);
      expect(result.serverAvailable).toBe(true);
      expect(result.useLocalOllama).toBe(false);
    });
    
    test('should handle case when neither service is available', async () => {
      ollamaService.checkOllamaStatus.mockResolvedValue(false);
      apiService.checkServerStatus.mockResolvedValue(false);
      
      const result = await initProcessingService();
      
      expect(result.ollamaAvailable).toBe(false);
      expect(result.serverAvailable).toBe(false);
      expect(result.useLocalOllama).toBe(false);
    });
  });
  
  describe('processItinerary', () => {
    test('should use local Ollama when available', async () => {
      ollamaService.checkOllamaStatus.mockResolvedValue(true);
      apiService.checkServerStatus.mockResolvedValue(true);
      
      const mockResponse = { success: true, calendarData: { summary: 'Test' } };
      ollamaService.processItinerary.mockResolvedValue(mockResponse);
      
      await initProcessingService();
      const result = await processItinerary('test text');
      
      expect(ollamaService.processItinerary).toHaveBeenCalledWith('test text');
      expect(apiService.processItinerary).not.toHaveBeenCalled();
      expect(result).toEqual(mockResponse);
    });
    
    test('should use backend API when Ollama is not available', async () => {
      ollamaService.checkOllamaStatus.mockResolvedValue(false);
      apiService.checkServerStatus.mockResolvedValue(true);
      
      const mockResponse = { success: true, calendarData: { summary: 'Test' } };
      apiService.processItinerary.mockResolvedValue(mockResponse);
      
      await initProcessingService();
      const result = await processItinerary('test text');
      
      expect(ollamaService.processItinerary).not.toHaveBeenCalled();
      expect(apiService.processItinerary).toHaveBeenCalledWith('test text');
      expect(result).toEqual(mockResponse);
    });
    
    test('should return error when neither service is available', async () => {
      ollamaService.checkOllamaStatus.mockResolvedValue(false);
      apiService.checkServerStatus.mockResolvedValue(false);
      
      await initProcessingService();
      const result = await processItinerary('test text');
      
      expect(result.success).toBe(false);
      expect(result.message).toContain('No processing service available');
    });
  });
  
  describe('checkStatus', () => {
    test('should return current status of services', async () => {
      ollamaService.checkOllamaStatus.mockResolvedValue(true);
      apiService.checkServerStatus.mockResolvedValue(false);
      
      const result = await checkStatus();
      
      expect(result.ollamaAvailable).toBe(true);
      expect(result.serverAvailable).toBe(false);
      expect(result.useLocalOllama).toBe(true);
    });
    
    test('should update status when services change', async () => {
      // First check - Ollama available
      ollamaService.checkOllamaStatus.mockResolvedValue(true);
      apiService.checkServerStatus.mockResolvedValue(false);
      
      await checkStatus();
      
      // Second check - Ollama not available
      ollamaService.checkOllamaStatus.mockResolvedValue(false);
      apiService.checkServerStatus.mockResolvedValue(true);
      
      const result = await checkStatus();
      
      expect(result.ollamaAvailable).toBe(false);
      expect(result.serverAvailable).toBe(true);
      expect(result.useLocalOllama).toBe(false);
    });
  });
});
