import { useState } from 'react';
import { Link, useNavigate,useSearchParams} from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import AuthShell from '../../components/layout/AuthShell';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
const justRegistered = searchParams.get('registered') === '1';
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Sign-in failed. Check the email and password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title="Sign in" subtitle="Use the account issued for your college.">
      <form className="auth-form" onSubmit={handleSubmit}>
        {justRegistered && (
  <p className="form-note form-note--ok" role="status">
    Account created — sign in to continue.
  </p>
)}
        <div className="form-group">
          <label className="form-label" htmlFor="login-email">Email</label>
          <input id="login-email" className="form-control" type="email" name="email" placeholder="you@college.edu" value={form.email} onChange={handleChange} required autoComplete="email" />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="login-password">Password</label>
          <input id="login-password" className="form-control" type="password" name="password" placeholder="Password" value={form.password} onChange={handleChange} required autoComplete="current-password" />
        </div>
        {error && <p className="form-error">{error}</p>}
        <button id="login-submit" className="btn btn--primary btn--lg" type="submit" disabled={loading}>
          {loading ? <span className="spinner" /> : 'Sign in'}
        </button>
      </form>
      <p className="text-sm text-muted" style={{ marginTop: '1rem' }}>
        New here? <Link to="/register" className="text-brand">Create an account</Link>
      </p>
      <p className="auth-hint">
        Local demo account<br />
        <strong>admin@clubhub.dev</strong> / <strong>admin1234</strong>
      </p>
    </AuthShell>
  );
}
