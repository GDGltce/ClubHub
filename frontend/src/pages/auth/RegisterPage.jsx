import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import AuthShell from '../../components/layout/AuthShell';

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password.length < 8) return setError('Use at least 8 characters.');
    if (form.password !== form.confirm) return setError('Those passwords do not match.');
    setLoading(true);
    try {
      await register(form.email, form.password, form.full_name);
      navigate('/login?registered=1');
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Registration failed. Try a different email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title="Create an account" subtitle="Students can join clubs after they register.">
      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="reg-name">Full name</label>
          <input id="reg-name" className="form-control" type="text" name="full_name" placeholder="Your name" value={form.full_name} onChange={handleChange} required autoComplete="name" />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="reg-email">Email</label>
          <input id="reg-email" className="form-control" type="email" name="email" placeholder="you@college.edu" value={form.email} onChange={handleChange} required autoComplete="email" />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="reg-pass">Password</label>
          <input id="reg-pass" className="form-control" type="password" name="password" placeholder="At least 8 characters" value={form.password} onChange={handleChange} required autoComplete="new-password" />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="reg-confirm">Confirm password</label>
          <input id="reg-confirm" className="form-control" type="password" name="confirm" placeholder="Repeat password" value={form.confirm} onChange={handleChange} required autoComplete="new-password" />
        </div>
        {error && <p className="form-error">{error}</p>}
        <button id="register-submit" className="btn btn--primary btn--lg" type="submit" disabled={loading}>
          {loading ? <span className="spinner" /> : 'Create account'}
        </button>
      </form>
      <p className="text-sm text-muted" style={{ marginTop: '1rem' }}>
        Already registered? <Link to="/login" className="text-brand">Sign in</Link>
      </p>
    </AuthShell>
  );
}
