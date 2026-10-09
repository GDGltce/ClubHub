import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import AppLayout from '../../components/layout/AppLayout';
import { eventApi, clubApi } from '../../api';
import { useAuth } from '../../contexts/AuthContext';

export default function EventCreatePage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const prefillClub = searchParams.get('club_id') || '';

  const [clubs, setClubs] = useState([]);
  const [form, setForm] = useState({
    club_id: prefillClub,
    title: '',
    description: '',
    goal: '',
    audience: '',
    expected_turnout: '',
    venue: '',
    start_datetime: '',
    end_datetime: '',
    visibility: 'public',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) navigate('/login');
    clubApi.list().then(r => setClubs(r.data)).catch(() => {});
  }, [user, navigate]);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = { ...form, expected_turnout: form.expected_turnout ? +form.expected_turnout : null };
      if (!payload.start_datetime) delete payload.start_datetime;
      if (!payload.end_datetime) delete payload.end_datetime;
      const { data } = await eventApi.create(payload);
      navigate(`/events/${data.id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create event');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="animate-fadeUp" style={{ maxWidth: 640, margin: '0 auto' }}>
        <div className="page-header">
          <div>
            <p className="page-kicker">Calendar</p>
            <h1 className="page-title">Create an event</h1>
            <p className="page-subtitle">It starts in the idea stage.</p>
          </div>
        </div>
        <div className="card">
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Club *</label>
              <select id="event-club" className="form-control" name="club_id" value={form.club_id} onChange={handleChange} required>
                <option value="">Select a club</option>
                {clubs.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Event Title *</label>
              <input id="event-title" className="form-control" name="title" value={form.title} onChange={handleChange} placeholder="e.g. HackNight 2026" required />
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Start Date & Time</label>
                <input className="form-control" type="datetime-local" name="start_datetime" value={form.start_datetime} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="form-label">End Date & Time</label>
                <input className="form-control" type="datetime-local" name="end_datetime" value={form.end_datetime} onChange={handleChange} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea id="event-desc" className="form-control" name="description" rows={3} value={form.description} onChange={handleChange} placeholder="What is this event about?" />
            </div>
            <div className="form-group">
              <label className="form-label">Goal</label>
              <input className="form-control" name="goal" value={form.goal} onChange={handleChange} placeholder="What do you want to achieve?" />
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Venue</label>
                <input className="form-control" name="venue" value={form.venue} onChange={handleChange} placeholder="Seminar Hall A" />
              </div>
              <div className="form-group">
                <label className="form-label">Expected Turnout</label>
                <input className="form-control" type="number" name="expected_turnout" value={form.expected_turnout} onChange={handleChange} placeholder="150" />
              </div>
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Audience</label>
                <input className="form-control" name="audience" value={form.audience} onChange={handleChange} placeholder="All Students, CSE Dept" />
              </div>
              <div className="form-group">
                <label className="form-label">Visibility</label>
                <select className="form-control" name="visibility" value={form.visibility} onChange={handleChange}>
                  <option value="public">Public</option>
                  <option value="members_only">Members Only</option>
                  <option value="club_leads_only">Club Leads Only</option>
                </select>
              </div>
            </div>
            {error && <p className="form-error">{error}</p>}
            <button id="create-event-submit" className="btn btn--primary" type="submit" disabled={loading}>
              {loading ? <span className="spinner" /> : 'Create event'}
            </button>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}
