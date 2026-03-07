import React, { useState } from 'react';
import Chatbot from '../components/Chatbot';

const API_URL = process.env.NODE_ENV === 'production'
  ? 'https://your-backend.onrender.com'
  : '';

// ─── Translation Panel ────────────────────────────────────────────────────────
function TranslationPanel({ apiUrl }) {
  const [isTranslating, setIsTranslating] = useState(false);
  const [translatedText, setTranslatedText] = useState('');
  const [error, setError] = useState('');

  const translate = async () => {
    const pageText =
      document.querySelector('article')?.innerText ||
      document.querySelector('.markdown')?.innerText || '';
    if (!pageText.trim()) { setError('No page content found.'); return; }

    const token = localStorage.getItem('auth_token');
    if (!token) { setError('Please sign in to use translation.'); return; }

    setIsTranslating(true);
    setError('');
    setTranslatedText('');

    try {
      const res = await fetch(`${apiUrl}/translation/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          text: pageText.substring(0, 5000),
          target_lang: 'ur',
          use_cache: true,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Translation failed');
      setTranslatedText(data.translated_text);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsTranslating(false);
    }
  };

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', height: '100%', overflowY: 'auto', background: '#fff' }}>
      <div style={{ fontWeight: 700, fontSize: '15px', color: '#4f46e5' }}>🌐 Urdu Translation</div>
      <p style={{ margin: 0, fontSize: '13px', color: '#666', lineHeight: 1.5 }}>
        Translate this chapter's content to Urdu (اردو). Sign in required.
      </p>

      {error && (
        <div style={{ background: '#fef2f2', color: '#dc2626', padding: '8px 12px', borderRadius: '8px', fontSize: '13px' }}>
          {error}
        </div>
      )}

      <button
        onClick={translate}
        disabled={isTranslating}
        style={{
          background: isTranslating ? '#a5b4fc' : 'linear-gradient(135deg, #4f46e5, #6366f1)',
          color: '#fff', border: 'none', borderRadius: '8px',
          padding: '10px 16px', cursor: isTranslating ? 'not-allowed' : 'pointer',
          fontWeight: 600, fontSize: '14px',
        }}
      >
        {isTranslating ? 'Translating…' : '🌐 Translate to Urdu (اردو)'}
      </button>

      {translatedText && (
        <div style={{
          background: '#f8f7ff', borderRadius: '10px', padding: '14px',
          fontSize: '14px', lineHeight: 1.8, direction: 'rtl', textAlign: 'right',
          color: '#1e1b4b', border: '1px solid rgba(79,70,229,0.15)',
          whiteSpace: 'pre-wrap',
        }}>
          <div style={{ fontSize: '11px', color: '#6366f1', marginBottom: '8px', direction: 'ltr', textAlign: 'left', fontWeight: 600 }}>
            ترجمہ:
          </div>
          {translatedText}
        </div>
      )}
    </div>
  );
}

// ─── Personalization Panel ────────────────────────────────────────────────────
function PersonalizationPanel({ apiUrl }) {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const personalize = async () => {
    const pageText =
      document.querySelector('article')?.innerText ||
      document.querySelector('.markdown')?.innerText || '';
    const title = document.querySelector('h1')?.innerText || '';

    if (!pageText.trim()) { setError('No page content found.'); return; }

    const token = localStorage.getItem('auth_token');
    if (!token) { setError('Please sign in to personalize content.'); return; }

    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch(`${apiUrl}/personalization/personalize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          chapter_content: pageText.substring(0, 4000),
          chapter_title: title,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Personalization failed');
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', height: '100%', overflowY: 'auto', background: '#fff' }}>
      <div style={{ fontWeight: 700, fontSize: '15px', color: '#4f46e5' }}>🎯 Personalize Chapter</div>
      <p style={{ margin: 0, fontSize: '13px', color: '#666', lineHeight: 1.5 }}>
        Adapt this chapter to your expertise level and background. Sign in required.
      </p>

      {error && (
        <div style={{ background: '#fef2f2', color: '#dc2626', padding: '8px 12px', borderRadius: '8px', fontSize: '13px' }}>
          {error}
        </div>
      )}

      <button
        onClick={personalize}
        disabled={isLoading}
        style={{
          background: isLoading ? '#a5b4fc' : 'linear-gradient(135deg, #4f46e5, #6366f1)',
          color: '#fff', border: 'none', borderRadius: '8px',
          padding: '10px 16px', cursor: isLoading ? 'not-allowed' : 'pointer',
          fontWeight: 600, fontSize: '14px',
        }}
      >
        {isLoading ? 'Personalizing…' : '🎯 Personalize This Chapter'}
      </button>

      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ background: '#ede9fe', color: '#4f46e5', borderRadius: '20px', padding: '4px 12px', fontSize: '12px', fontWeight: 600 }}>
              {result.expertise_level}
            </span>
            <span style={{ background: '#ede9fe', color: '#4f46e5', borderRadius: '20px', padding: '4px 12px', fontSize: '12px', fontWeight: 600 }}>
              {result.background}
            </span>
          </div>
          <div style={{ fontSize: '12px', color: '#555' }}>
            <strong>Adaptations applied:</strong>
            <ul style={{ margin: '4px 0 0', paddingLeft: '18px' }}>
              {result.adaptations_applied.map((a, i) => <li key={i}>{a}</li>)}
            </ul>
          </div>
          <div style={{
            background: '#f8f7ff', borderRadius: '10px', padding: '14px',
            fontSize: '13px', lineHeight: 1.7, color: '#1e1b4b',
            border: '1px solid rgba(79,70,229,0.15)',
            maxHeight: '280px', overflowY: 'auto', whiteSpace: 'pre-wrap',
          }}>
            {result.personalized_content}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Root ─────────────────────────────────────────────────────────────────────
export default function Root({ children }) {
  const [chatOpen, setChatOpen] = useState(false);
  const [translateOpen, setTranslateOpen] = useState(false);
  const [personalizeOpen, setPersonalizeOpen] = useState(false);

  const toggle = (panel) => {
    if (panel === 'chat') {
      const next = !chatOpen;
      setChatOpen(next);
      if (next) { setTranslateOpen(false); setPersonalizeOpen(false); }
    } else if (panel === 'translate') {
      const next = !translateOpen;
      setTranslateOpen(next);
      if (next) { setChatOpen(false); setPersonalizeOpen(false); }
    } else if (panel === 'personalize') {
      const next = !personalizeOpen;
      setPersonalizeOpen(next);
      if (next) { setChatOpen(false); setTranslateOpen(false); }
    }
  };

  const panelWrap = {
    position: 'fixed', bottom: '92px', right: '28px',
    width: '370px', maxHeight: '68vh', zIndex: 9998,
    boxShadow: '0 12px 40px rgba(0,0,0,0.18)',
    borderRadius: '14px', overflow: 'hidden',
    display: 'flex', flexDirection: 'column',
    border: '1px solid rgba(79,70,229,0.15)',
    background: '#fff',
  };

  const makeBtn = (active, emoji, title) => ({
    button: {
      width: '52px', height: '52px', borderRadius: '50%',
      background: active
        ? 'linear-gradient(135deg, #3730a3, #4338ca)'
        : 'linear-gradient(135deg, #4f46e5, #6366f1)',
      color: '#fff', border: 'none', fontSize: '22px',
      cursor: 'pointer',
      boxShadow: '0 4px 20px rgba(79,70,229,0.45)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      transition: 'transform 0.2s',
      outline: 'none',
    },
    emoji,
    title,
  });

  return (
    <>
      {children}

      {/* Panels */}
      {chatOpen && (
        <div style={panelWrap}>
          <Chatbot apiUrl={API_URL} />
        </div>
      )}
      {translateOpen && (
        <div style={panelWrap}>
          <TranslationPanel apiUrl={API_URL} />
        </div>
      )}
      {personalizeOpen && (
        <div style={panelWrap}>
          <PersonalizationPanel apiUrl={API_URL} />
        </div>
      )}

      {/* Floating button group — bottom right */}
      <div style={{
        position: 'fixed', bottom: '28px', right: '28px',
        display: 'flex', flexDirection: 'column', gap: '10px', zIndex: 9999,
        alignItems: 'center',
      }}>
        {/* Personalize */}
        <button
          title="Personalize Chapter"
          onClick={() => toggle('personalize')}
          style={{
            width: '48px', height: '48px', borderRadius: '50%',
            background: personalizeOpen
              ? 'linear-gradient(135deg, #3730a3, #4338ca)'
              : 'linear-gradient(135deg, #4f46e5, #6366f1)',
            color: '#fff', border: 'none', fontSize: '20px',
            cursor: 'pointer',
            boxShadow: '0 4px 16px rgba(79,70,229,0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'transform 0.2s',
          }}
          onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.08)'}
          onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
        >🎯</button>

        {/* Translate */}
        <button
          title="Translate to Urdu"
          onClick={() => toggle('translate')}
          style={{
            width: '48px', height: '48px', borderRadius: '50%',
            background: translateOpen
              ? 'linear-gradient(135deg, #3730a3, #4338ca)'
              : 'linear-gradient(135deg, #4f46e5, #6366f1)',
            color: '#fff', border: 'none', fontSize: '20px',
            cursor: 'pointer',
            boxShadow: '0 4px 16px rgba(79,70,229,0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'transform 0.2s',
          }}
          onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.08)'}
          onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
        >🌐</button>

        {/* Chatbot — main, slightly larger */}
        <button
          title={chatOpen ? 'Close AI Tutor' : 'Open AI Tutor'}
          onClick={() => toggle('chat')}
          style={{
            width: '54px', height: '54px', borderRadius: '50%',
            background: chatOpen
              ? 'linear-gradient(135deg, #3730a3, #4338ca)'
              : 'linear-gradient(135deg, #4f46e5, #6366f1)',
            color: '#fff', border: 'none', fontSize: chatOpen ? '18px' : '24px',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(79,70,229,0.5)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'transform 0.2s',
          }}
          onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.08)'}
          onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
        >{chatOpen ? '✕' : '🤖'}</button>
      </div>
    </>
  );
}
