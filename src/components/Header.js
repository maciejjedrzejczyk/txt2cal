import React from 'react';
import OllamaStatus from './OllamaStatus';

/**
 * Header component with app title and status indicator
 */
function Header() {
  return (
    <header className="app-header">
      <div className="header-content">
        <h1 className="app-title">
          <span className="title-text">txt2cal</span>
          <span className="title-subtitle">Text to Calendar Converter</span>
        </h1>
        <OllamaStatus />
      </div>
    </header>
  );
}

export default Header;
