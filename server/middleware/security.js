/**
 * Security middleware
 */

const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

/**
 * Configure CORS
 */
const corsOptions = {
  origin: process.env.CORS_ORIGIN || '*',
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400 // 24 hours
};

/**
 * Configure rate limiting
 */
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    message: 'Too many requests from this IP, please try again later'
  }
});

/**
 * Apply security middleware to an Express app
 * @param {Object} app - Express app
 */
const applySecurityMiddleware = (app) => {
  // Use Helmet for security headers
  app.use(helmet());
  
  // Enable CORS
  app.use(cors(corsOptions));
  
  // Apply rate limiting to API routes
  app.use('/api/', apiLimiter);
  
  // Prevent clickjacking
  app.use((req, res, next) => {
    res.setHeader('X-Frame-Options', 'DENY');
    next();
  });
  
  // Content Security Policy
  if (process.env.NODE_ENV === 'production') {
    app.use(helmet.contentSecurityPolicy({
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", 'data:'],
        connectSrc: ["'self'", 'https://maps.googleapis.com'],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        mediaSrc: ["'none'"],
        frameSrc: ["'none'"]
      }
    }));
  }
};

module.exports = {
  applySecurityMiddleware
};
