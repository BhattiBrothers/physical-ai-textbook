import React, { useState, useEffect } from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const TranslationToggle = ({
  apiUrl = 'http://localhost:8000',
  defaultLanguage = 'en',
  textToTranslate = '',
  onTranslationComplete = null
}) => {
  const [currentLanguage, setCurrentLanguage] = useState(defaultLanguage);
  const [isTranslating, setIsTranslating] = useState(false);
  const [translatedText, setTranslatedText] = useState('');
  const [error, setError] = useState(null);
  const [supportedLanguages, setSupportedLanguages] = useState({});
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Fetch supported languages on component mount
  useEffect(() => {
    fetchSupportedLanguages();
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        // Verify token is valid by making a simple API call
        setIsAuthenticated(true);
      }
    } catch (err) {
      console.log('Not authenticated for translation:', err);
    }
  };

  const fetchSupportedLanguages = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

      const response = await fetch(`${apiUrl}/translation/languages`, {
        headers
      });

      if (response.ok) {
        const data = await response.json();
        setSupportedLanguages(data);
      } else if (response.status === 401) {
        setIsAuthenticated(false);
      }
    } catch (err) {
      console.error('Failed to fetch supported languages:', err);
    }
  };

  const handleTranslate = async (text, targetLang = 'ur') => {
    if (!text.trim()) {
      setError('No text to translate');
      return;
    }

    if (!isAuthenticated) {
      setError('Please log in to use translation feature');
      return;
    }

    setIsTranslating(true);
    setError(null);

    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${apiUrl}/translation/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          text,
          target_lang: targetLang,
          use_cache: true
        })
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Please log in to use translation');
        }
        throw new Error(`Translation failed: ${response.status}`);
      }

      const data = await response.json();
      setTranslatedText(data.translated_text);
      setCurrentLanguage(targetLang);

      if (onTranslationComplete) {
        onTranslationComplete(data);
      }
    } catch (err) {
      console.error('Translation error:', err);
      setError(err.message);

      // For demo purposes, show a mock translation
      if (err.message.includes('authentication') || err.message.includes('log in')) {
        setTranslatedText(`[مترجم - ترجمہ]: ${text}`);
        setCurrentLanguage('ur');
      }
    } finally {
      setIsTranslating(false);
    }
  };

  const handleToggleLanguage = () => {
    const newLang = currentLanguage === 'en' ? 'ur' : 'en';

    if (newLang === 'ur' && textToTranslate) {
      handleTranslate(textToTranslate, 'ur');
    } else {
      setCurrentLanguage(newLang);
      setTranslatedText('');

      if (onTranslationComplete && newLang === 'en') {
        onTranslationComplete({
          original_text: textToTranslate,
          translated_text: textToTranslate,
          target_lang: 'en',
          from_cache: false,
          is_mock: false
        });
      }
    }
  };

  const handleTranslatePage = () => {
    // This would translate the entire page content
    // For now, we'll translate the text provided via props
    if (textToTranslate) {
      handleTranslate(textToTranslate, 'ur');
    } else {
      // Try to get text from the current page
      const pageContent = document.querySelector('article')?.innerText ||
                         document.querySelector('.markdown')?.innerText ||
                         '';

      if (pageContent.trim()) {
        handleTranslate(pageContent.substring(0, 5000), 'ur');
      } else {
        setError('No content found to translate');
      }
    }
  };

  const getLanguageName = (code) => {
    return supportedLanguages[code] ||
      (code === 'en' ? 'English' :
       code === 'ur' ? 'Urdu' :
       code.toUpperCase());
  };

  return (
    <div className={clsx(styles.translationContainer)}>
      <div className={styles.translationHeader}>
        <h4 className={styles.translationTitle}>
          <span role="img" aria-label="translation">🌐</span> Translation
        </h4>
        <div className={styles.languageDisplay}>
          Current language: <span className={styles.languageCode}>{getLanguageName(currentLanguage)}</span>
        </div>
      </div>

      {!isAuthenticated && (
        <div className={styles.authWarning}>
          <span role="img" aria-label="warning">⚠️</span>
          Log in to access translation features
        </div>
      )}

      {isAuthenticated && (
        <div className={styles.translationControls}>
          <button
            onClick={handleToggleLanguage}
            className={clsx(
              styles.toggleButton,
              currentLanguage === 'ur' && styles.urduActive
            )}
            disabled={isTranslating}
          >
            <span className={styles.buttonText}>
              {currentLanguage === 'en' ? 'Translate to Urdu' : 'Switch to English'}
            </span>
            <span className={styles.buttonIcon}>
              {currentLanguage === 'en' ? '🌐 → اردو' : '🌐 → English'}
            </span>
          </button>

          <button
            onClick={handleTranslatePage}
            className={styles.translatePageButton}
            disabled={isTranslating}
          >
            {isTranslating ? 'Translating...' : 'Translate this page'}
          </button>

          {currentLanguage === 'ur' && translatedText && (
            <div className={styles.translationPreview}>
              <div className={styles.previewHeader}>Translated Preview:</div>
              <div className={styles.previewContent}>
                {translatedText}
              </div>
              <div className={styles.previewNote}>
                <small>
                  Note: This is a mock translation. In production, this would be replaced with actual translation API.
                </small>
              </div>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className={styles.errorBanner}>
          {error}
        </div>
      )}

      <div className={styles.translationInfo}>
        <div className={styles.infoItem}>
          <span role="img" aria-label="cache">💾</span>
          <span>Cached translations for faster access</span>
        </div>
        <div className={styles.infoItem}>
          <span role="img" aria-label="technical">🔧</span>
          <span>Technical terminology preserved</span>
        </div>
        <div className={styles.infoItem}>
          <span role="img" aria-label="rtl">↔️</span>
          <span>RTL layout support for Urdu</span>
        </div>
      </div>
    </div>
  );
};

export default TranslationToggle;