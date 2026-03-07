import React, { useState, useEffect } from 'react';
import useBaseUrl from '@docusaurus/useBaseUrl';

export default function AuthNavbarItem({ mobile = false }) {
  const [user, setUser] = useState(null);
  const loginUrl = useBaseUrl('/login');

  useEffect(() => {
    const sync = () => {
      try {
        const stored = localStorage.getItem('user_profile');
        setUser(stored ? JSON.parse(stored) : null);
      } catch { setUser(null); }
    };
    sync();
    window.addEventListener('storage', sync);
    window.addEventListener('focus', sync);
    return () => {
      window.removeEventListener('storage', sync);
      window.removeEventListener('focus', sync);
    };
  }, []);

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_profile');
    window.dispatchEvent(new Event('storage'));
    setUser(null);
    window.location.href = loginUrl;
  };

  const initials = user
    ? (user.full_name
        ? user.full_name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
        : user.username.slice(0, 2).toUpperCase())
    : '';

  if (mobile) {
    return user ? (
      <div style={{ padding: '0.4rem 0' }}>
        <a href={loginUrl} style={{ display: 'block', fontWeight: 600, marginBottom: '0.3rem' }}>
          {user.full_name || user.username}
        </a>
        <button onClick={logout} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#b91c1c', padding: 0, fontSize: '0.9rem' }}>
          Log out
        </button>
      </div>
    ) : (
      <a href={loginUrl} style={{ fontWeight: 600 }}>Sign In</a>
    );
  }

  if (user) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <a href={loginUrl} style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', color: 'inherit' }}>
          <div style={{
            width: '30px', height: '30px', borderRadius: '50%',
            background: 'linear-gradient(135deg, #4f46e5, #06b6d4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#fff', fontSize: '0.7rem', fontWeight: 700,
          }}>
            {initials}
          </div>
          <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>
            {user.full_name || user.username}
          </span>
        </a>
        <button onClick={logout} style={{
          background: 'transparent',
          border: '1px solid rgba(185,28,28,0.35)',
          color: '#b91c1c',
          borderRadius: '6px',
          padding: '3px 10px',
          cursor: 'pointer',
          fontSize: '0.8rem',
          fontWeight: 500,
        }}>
          Logout
        </button>
      </div>
    );
  }

  return (
    <a href={loginUrl} style={{
      padding: '6px 16px',
      background: 'linear-gradient(135deg, #4f46e5, #6366f1)',
      color: '#fff',
      borderRadius: '7px',
      fontWeight: 600,
      fontSize: '0.88rem',
      textDecoration: 'none',
      transition: 'opacity 0.2s',
    }}>
      Sign In
    </a>
  );
}
