import React from 'react';

/**
 * Footer component with links and information
 */
function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-links">
          <a 
            href="https://github.com/maciejjedrzejczyk/txt2cal" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            GitHub
          </a>
          <span className="footer-separator">|</span>
          <a 
            href="https://github.com/maciejjedrzejczyk/txt2cal/issues" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            Report Issue
          </a>
          <span className="footer-separator">|</span>
          <button 
            className="theme-toggle"
            onClick={() => document.body.classList.toggle('dark-mode')}
            aria-label="Toggle dark mode"
          >
            Toggle Dark Mode
          </button>
        </div>
        <div className="footer-copyright">
          &copy; {new Date().getFullYear()} txt2cal - MIT License
        </div>
      </div>
    </footer>
  );
}

export default Footer;
