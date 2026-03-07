import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './login.module.css';

const API_URL = process.env.NODE_ENV === 'production'
  ? 'https://your-backend.onrender.com'
  : '';

function getInitials(user) {
  if (user.full_name) {
    return user.full_name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
  }
  return user.username.slice(0, 2).toUpperCase();
}

function LoginPage() {
  const textbookUrl = useBaseUrl('/docs/intro');
  const [mode, setMode] = useState('login');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [form, setForm] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    expertise_level: 'beginner',
    background: 'both',
    preferred_language: 'en',
  });

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const stored = localStorage.getItem('user_profile');
    if (token && stored) {
      try { setUser(JSON.parse(stored)); } catch {}
    }
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: form.email, password: form.password }).toString(),
      });
      let data;
      try { data = await res.json(); } catch { data = {}; }
      if (!res.ok) throw new Error(data.detail || 'Login failed');
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('user_profile', JSON.stringify(data.user));
      setUser(data.user);
      window.dispatchEvent(new Event('storage'));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      let data;
      try { data = await res.json(); } catch { data = {}; }
      if (!res.ok) throw new Error(data.detail || `Registration failed (${res.status})`);
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('user_profile', JSON.stringify(data.user));
      setUser(data.user);
      window.dispatchEvent(new Event('storage'));
      setSuccess('Account created successfully!');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_profile');
    window.dispatchEvent(new Event('storage'));
    setUser(null);
  };

  // ── Profile view ──
  if (user) {
    return (
      <Layout title="Profile" description="Your account profile">
        <div className={styles.page}>
          {/* Left branding */}
          <div className={styles.brand}>
            <div className={styles.brandLogo}>🤖</div>
            <h1 className={styles.brandTitle}>Physical AI &amp; Humanoid Robotics</h1>
            <p className={styles.brandSub}>Your personalised AI-native textbook experience</p>
            <ul className={styles.brandFeatures}>
              <li>RAG-powered AI Tutor chatbot</li>
              <li>Content adapted to your expertise</li>
              <li>Urdu translation support</li>
              <li>Progress tracking &amp; personalization</li>
            </ul>
          </div>

          {/* Right profile */}
          <div className={styles.formPanel}>
            <div className={styles.card}>
              <div className={styles.profileHeader}>
                <div className={styles.avatar}>{getInitials(user)}</div>
                <div>
                  <p className={styles.profileName}>{user.full_name || user.username}</p>
                  <p className={styles.profileEmail}>{user.email}</p>
                </div>
              </div>

              <div className={styles.profileGrid}>
                <div className={styles.profileItem}>
                  <span className={styles.label}>Username</span>
                  <span>@{user.username}</span>
                </div>
                <div className={styles.profileItem}>
                  <span className={styles.label}>Expertise</span>
                  <span className={styles.badge}>{user.expertise_level}</span>
                </div>
                <div className={styles.profileItem}>
                  <span className={styles.label}>Background</span>
                  <span className={styles.badge}>{user.background}</span>
                </div>
                <div className={styles.profileItem}>
                  <span className={styles.label}>Language</span>
                  <span>{user.preferred_language === 'ur' ? 'اردو' : 'English'}</span>
                </div>
              </div>

              <div className={styles.featureList}>
                <h3>Active Features</h3>
                <ul>
                  <li>✅ RAG Chatbot — Ask questions about the textbook</li>
                  <li>✅ Personalized content by expertise level</li>
                  <li>✅ Urdu translation</li>
                </ul>
              </div>

              {success && <div className={styles.success}>{success}</div>}

              <div className={styles.actions}>
                <a href={textbookUrl} className={styles.primaryBtn}>
                  Open Textbook →
                </a>
                <button className={styles.logoutBtn} onClick={handleLogout}>
                  Log Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // ── Auth view ──
  return (
    <Layout title="Sign In" description="Sign in to your account">
      <div className={styles.page}>
        {/* Left branding */}
        <div className={styles.brand}>
          <div className={styles.brandLogo}>🤖</div>
          <h1 className={styles.brandTitle}>Physical AI &amp; Humanoid Robotics</h1>
          <p className={styles.brandSub}>
            An AI-native textbook designed to teach you embodied intelligence and robotic systems.
          </p>
          <ul className={styles.brandFeatures}>
            <li>RAG-powered AI Tutor chatbot</li>
            <li>Content adapted to your expertise</li>
            <li>Urdu translation support</li>
            <li>Progress tracking &amp; personalization</li>
          </ul>
        </div>

        {/* Right form */}
        <div className={styles.formPanel}>
          <div className={styles.card}>
            <h2 className={styles.cardTitle}>
              {mode === 'login' ? 'Welcome back' : 'Create account'}
            </h2>
            <p className={styles.cardSub}>
              {mode === 'login'
                ? 'Sign in to continue your learning journey'
                : 'Join to unlock your personalised experience'}
            </p>

            <div className={styles.tabBar}>
              <button
                className={mode === 'login' ? styles.activeTab : styles.tab}
                onClick={() => { setMode('login'); setError(''); }}
              >Sign In</button>
              <button
                className={mode === 'register' ? styles.activeTab : styles.tab}
                onClick={() => { setMode('register'); setError(''); }}
              >Register</button>
            </div>

            {error && <div className={styles.error}>{error}</div>}
            {success && <div className={styles.success}>{success}</div>}

            <form onSubmit={mode === 'login' ? handleLogin : handleRegister}>
              <div className={styles.field}>
                <label>Email address</label>
                <input
                  type="email" name="email" required
                  value={form.email} onChange={handleChange}
                  placeholder="you@example.com"
                />
              </div>

              {mode === 'register' && (
                <>
                  <div className={styles.field}>
                    <label>Username</label>
                    <input
                      type="text" name="username" required
                      value={form.username} onChange={handleChange}
                      placeholder="your_username"
                    />
                  </div>
                  <div className={styles.field}>
                    <label>Full Name <span style={{opacity:0.5,fontWeight:400}}>(optional)</span></label>
                    <input
                      type="text" name="full_name"
                      value={form.full_name} onChange={handleChange}
                      placeholder="Your Name"
                    />
                  </div>
                </>
              )}

              <div className={styles.field}>
                <label>Password</label>
                <input
                  type="password" name="password" required
                  value={form.password} onChange={handleChange}
                  placeholder="••••••••" minLength={6}
                />
              </div>

              {mode === 'register' && (
                <>
                  <div className={styles.field}>
                    <label>Expertise Level</label>
                    <select name="expertise_level" value={form.expertise_level} onChange={handleChange}>
                      <option value="beginner">Beginner — New to robotics</option>
                      <option value="intermediate">Intermediate — Some experience</option>
                      <option value="expert">Expert — Professional background</option>
                    </select>
                  </div>
                  <div className={styles.field}>
                    <label>Background</label>
                    <select name="background" value={form.background} onChange={handleChange}>
                      <option value="software">Software — CS / Programming</option>
                      <option value="hardware">Hardware — EE / Mechanical</option>
                      <option value="both">Both — Mixed background</option>
                    </select>
                  </div>
                  <div className={styles.field}>
                    <label>Preferred Language</label>
                    <select name="preferred_language" value={form.preferred_language} onChange={handleChange}>
                      <option value="en">English</option>
                      <option value="ur">اردو (Urdu)</option>
                    </select>
                  </div>
                </>
              )}

              <button type="submit" className={styles.submitBtn} disabled={loading}>
                {loading ? 'Please wait…' : (mode === 'login' ? 'Sign In' : 'Create Account')}
              </button>
            </form>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default LoginPage;
