/**
 * Error handling middleware
 */

const fs = require('fs');
const path = require('path');
const LOG_DIR = path.join(__dirname, '../logs');

// Ensure log directory exists
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}

/**
 * Error logger middleware
 */
const errorLogger = (err, req, res, next) => {
  const timestamp = new Date().toISOString();
  const logEntry = `${timestamp} - ${req.method} ${req.url} - ${err.stack}\n`;
  
  // Log to console
  console.error(logEntry);
  
  // Log to file
  fs.appendFileSync(
    path.join(LOG_DIR, 'error.log'),
    logEntry
  );
  
  next(err);
};

/**
 * Error response middleware
 */
const errorResponder = (err, req, res, next) => {
  const status = err.statusCode || 500;
  
  res.status(status).json({
    success: false,
    message: err.message || 'Internal Server Error',
    error: process.env.NODE_ENV === 'production' ? undefined : err.stack
  });
};

/**
 * 404 handler middleware
 */
const notFoundHandler = (req, res) => {
  res.status(404).json({
    success: false,
    message: 'Resource not found'
  });
};

module.exports = {
  errorLogger,
  errorResponder,
  notFoundHandler
};
