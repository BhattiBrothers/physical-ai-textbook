import React from 'react';
import TranslationToggle from './index';

const TranslationToggleWidget = ({
  apiUrl = 'http://localhost:8000',
  defaultLanguage = 'en',
  textToTranslate = ''
}) => {
  // Get text from the page if not provided
  const getPageText = () => {
    if (typeof window !== 'undefined' && !textToTranslate) {
      // Try to get the main content of the page
      const article = document.querySelector('article');
      const mainContent = document.querySelector('.markdown');
      const container = article || mainContent || document.body;

      if (container) {
        // Get text content, limit to reasonable length
        return container.innerText.substring(0, 5000);
      }
    }
    return textToTranslate;
  };

  return (
    <div style={{ margin: '2rem 0' }}>
      <TranslationToggle
        apiUrl={apiUrl}
        defaultLanguage={defaultLanguage}
        textToTranslate={getPageText()}
        onTranslationComplete={(data) => {
          console.log('Translation completed:', data);
          // Could update page content here in a real implementation
        }}
      />
    </div>
  );
};

export default TranslationToggleWidget;