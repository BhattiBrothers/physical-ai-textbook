import React from 'react';
import Chatbot from './Chatbot';

/**
 * ChatbotWidget - A wrapper component for the chatbot that can be easily embedded in markdown.
 *
 * Usage in MDX:
 * ```jsx
 * import ChatbotWidget from '@site/src/components/ChatbotWidget';
 *
 * <ChatbotWidget />
 * ```
 *
 * Or with custom API URL:
 * ```jsx
 * <ChatbotWidget apiUrl="http://localhost:8000" />
 * ```
 */
const ChatbotWidget = ({ apiUrl = 'http://localhost:8000', height = '600px' }) => {
  // In production, you might want to use a different API URL
  const getApiUrl = () => {
    // You can customize this logic based on environment
    if (typeof window !== 'undefined') {
      // Check if we're in production
      if (window.location.hostname !== 'localhost') {
        // Use production API URL
        return 'https://your-production-api-url.com';
      }
    }
    return apiUrl;
  };

  const containerStyle = {
    margin: '2rem 0',
    borderRadius: '12px',
    overflow: 'hidden',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
    height: height
  };

  return (
    <div style={containerStyle}>
      <Chatbot apiUrl={getApiUrl()} />
    </div>
  );
};

export default ChatbotWidget;