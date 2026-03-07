import React, { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import ReactMarkdown from 'react-markdown';
import styles from './styles.module.css';

const Chatbot = ({ apiUrl = '' }) => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m your Physical AI & Humanoid Robotics tutor. How can I help you today?', timestamp: new Date() }
  ]);
  const [input, setInput] = useState('');
  const [selectedText, setSelectedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Get selected text from page
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection.toString().trim();
      if (text && text.length > 0) {
        setSelectedText(text);
      } else {
        setSelectedText('');
      }
    };

    document.addEventListener('selectionchange', handleSelection);
    return () => document.removeEventListener('selectionchange', handleSelection);
  }, []);

  const sendMessage = async (text, useSelectedText = false) => {
    if (!text.trim() && !useSelectedText) return;

    const userMessage = {
      role: 'user',
      content: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: text,
          selected_text: useSelectedText ? selectedText : null,
          conversation_id: conversationId
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Update conversation ID if new
      if (!conversationId && data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Clear selected text after using it
      if (useSelectedText) {
        setSelectedText('');
      }
    } catch (err) {
      console.error('Chat error:', err);
      setError(err.message);

      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or check if the backend server is running.',
        isError: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleAskAboutSelected = () => {
    if (selectedText) {
      sendMessage('Can you explain this?', true);
    }
  };

  const clearChat = () => {
    setMessages([
      { role: 'assistant', content: 'Hello! I\'m your Physical AI & Humanoid Robotics tutor. How can I help you today?', timestamp: new Date() }
    ]);
    setConversationId(null);
    setError(null);
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={clsx(styles.chatbotContainer)}>
      <div className={styles.chatbotHeader}>
        <h3 className={styles.chatbotTitle}>🤖 Physical AI Tutor</h3>
        <div className={styles.chatbotSubtitle}>Ask questions about the textbook</div>
        <button onClick={clearChat} className={styles.clearButton}>Clear Chat</button>
      </div>

      {selectedText && (
        <div className={styles.selectedTextBanner}>
          <div className={styles.selectedTextLabel}>Selected Text:</div>
          <div className={styles.selectedTextContent}>{selectedText}</div>
          <button
            onClick={handleAskAboutSelected}
            className={styles.askAboutButton}
          >
            Ask about selected text
          </button>
        </div>
      )}

      <div className={styles.messagesContainer}>
        {messages.map((message, index) => (
          <div
            key={index}
            className={clsx(
              styles.message,
              message.role === 'user' ? styles.userMessage : styles.assistantMessage,
              message.isError && styles.errorMessage
            )}
          >
            <div className={styles.messageHeader}>
              <span className={styles.messageRole}>
                {message.role === 'user' ? 'You' : 'AI Tutor'}
              </span>
              <span className={styles.messageTime}>
                {formatTime(new Date(message.timestamp))}
              </span>
            </div>
            <div className={styles.messageContent}>
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
            {message.sources && message.sources.length > 0 && (
              <div className={styles.messageSources}>
                <span className={styles.sourcesLabel}>Sources: </span>
                {message.sources.join(', ')}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className={styles.loadingMessage}>
            <div className={styles.thinkingIndicator}>Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className={styles.errorBanner}>
          Error: {error}. Make sure the backend server is running at {apiUrl}
        </div>
      )}

      <form onSubmit={handleSubmit} className={styles.inputForm}>
        <div className={styles.inputContainer}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about Physical AI or Humanoid Robotics..."
            className={styles.textInput}
            disabled={isLoading}
          />
          <button
            type="submit"
            className={styles.sendButton}
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </div>
        <div className={styles.inputHint}>
          Select text from the textbook and click "Ask about selected text"
        </div>
      </form>

      <div className={styles.chatbotFooter}>
        <div className={styles.footerNote}>
          Powered by RAG with OpenAI, Qdrant, and FastAPI
        </div>
      </div>
    </div>
  );
};

export default Chatbot;