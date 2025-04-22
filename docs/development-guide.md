# txt2cal Development Guide

This guide provides information for developers who want to contribute to or modify the txt2cal application.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Architecture Overview](#architecture-overview)
4. [Frontend Development](#frontend-development)
5. [Backend Development](#backend-development)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Contributing Guidelines](#contributing-guidelines)

## Development Environment Setup

### Prerequisites

- Node.js v16+ and npm v8+
- Git
- Ollama (for local development)

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/txt2cal.git
   cd txt2cal
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd server
   npm install
   cd ..
   ```

4. Set up environment variables:
   ```bash
   cp server/.env.example server/.env
   # Edit .env file as needed
   ```

5. Start the development servers:
   ```bash
   # Start both frontend and backend
   npm run dev
   
   # Or start them separately
   npm start          # Frontend
   npm run server     # Backend
   ```

6. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

7. Pull the required model:
   ```bash
   ollama pull llama3.2
   ```

## Project Structure

```
txt2cal/
├── public/           # Static files
├── server/           # Backend server
│   ├── middleware/   # Server middleware
│   ├── routes/       # API routes
│   ├── logs/         # Server logs
│   └── server.js     # Server entry point
├── src/              # Frontend source code
│   ├── components/   # UI components
│   ├── services/     # API services
│   ├── utils/        # Utility functions
│   ├── tests/        # Test files
│   ├── App.css       # Main styles
│   ├── App.js        # Main component
│   ├── index.css     # Global styles
│   └── index.js      # Entry point
├── docs/             # Documentation
├── README.md         # Project documentation
└── task-plan.md      # Development task plan
```

## Architecture Overview

txt2cal follows a client-server architecture with two processing paths:

1. **Direct Ollama Processing**: The frontend communicates directly with a locally running Ollama instance
2. **Backend Server Processing**: The frontend sends requests to the backend server, which communicates with Ollama

### Processing Flow

1. User inputs itinerary text
2. The application checks if local Ollama is available
   - If available, it sends the request directly to Ollama
   - If not, it sends the request to the backend server
3. The LLM processes the text and extracts calendar information
4. The application generates an ICS file from the extracted information
5. The user downloads and imports the ICS file into their calendar

## Frontend Development

### Key Components

- **App.js**: Main application component
- **ItineraryInput.js**: Text input and sample buttons
- **CalendarPreview.js**: Preview of extracted calendar event
- **OllamaStatus.js**: Status indicator for Ollama connection

### Services

- **ollamaService.js**: Direct communication with local Ollama
- **apiService.js**: Communication with the backend server
- **processingService.js**: Orchestrates between local and server processing

### Utilities

- **calendarUtils.js**: Functions for generating and validating ICS files
- **testUtils.js**: Sample data and testing utilities

### Adding a New Component

1. Create a new file in the `src/components` directory
2. Import and use the component in the appropriate parent component
3. Add styles in `App.css` or create a component-specific CSS file

### Modifying the UI

The application uses plain CSS for styling. All styles are in `src/App.css`.

## Backend Development

### Server Structure

- **server.js**: Main server entry point
- **routes/api.js**: API route definitions
- **middleware/**: Middleware functions for security, logging, etc.

### API Endpoints

- `GET /api/health`: Server health check
- `GET /api/ollama/status`: Check Ollama connection status
- `POST /api/process`: Process itinerary text

### Adding a New Endpoint

1. Add the route in `server/routes/api.js`
2. Implement the necessary logic
3. Update the API documentation in `docs/api-reference.md`

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Run specific tests
npm test -- -t "calendar utils"
```

### Writing Tests

1. Create test files in the `src/tests` directory
2. Use Jest for testing
3. Follow the existing test patterns

### Test Coverage

To generate a test coverage report:

```bash
npm test -- --coverage
```

## Deployment

### Frontend Deployment

1. Build the frontend:
   ```bash
   npm run build
   ```

2. Deploy the contents of the `build` directory to your web server

### Backend Deployment

1. Set up environment variables on your server
2. Install dependencies:
   ```bash
   cd server
   npm install --production
   ```

3. Start the server:
   ```bash
   NODE_ENV=production node server.js
   ```

4. For production, use a process manager like PM2:
   ```bash
   npm install -g pm2
   pm2 start server.js --name txt2cal-server
   ```

## Contributing Guidelines

### Code Style

- Use consistent indentation (2 spaces)
- Follow JavaScript best practices
- Add comments for complex logic
- Use descriptive variable and function names

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure they pass
5. Submit a pull request with a clear description of the changes

### Commit Messages

Follow the conventional commits format:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for code style changes
- `refactor:` for code refactoring
- `test:` for adding or modifying tests
- `chore:` for maintenance tasks

### Issue Reporting

When reporting issues, include:

1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Screenshots if applicable
5. Environment information (browser, OS, etc.)

## Additional Resources

- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Express.js Documentation](https://expressjs.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [iCalendar Format Specification](https://datatracker.ietf.org/doc/html/rfc5545)
