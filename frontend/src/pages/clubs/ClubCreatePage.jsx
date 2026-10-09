import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppLayout from '../../components/layout/AppLayout';
import { clubApi, institutionApi } from '../../api';

export default function ClubCreatePage() {
  const navigate = useNavigate();
  const [colleges, setColleges] = useState([]);
  const [form, setForm] = useState({
    college_id: '',
    name: '',
    short_name: '',
    description: '',
    tagline: '',
    club_type: 'departmental',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    institutionApi.listColleges().then((r) => setColleges(r.data)).catch(() => setError('Colleges could not be loaded.'));
  }, []);

  const handleChange = (e) => setForm((current) => ({ ...current, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = {
        ...form,
        short_name: form.short_name || null,
        description: form.description || null,
        tagline: form.tagline || null,
      };
      const { data } = await clubApi.create(payload);
      navigate(`/clubs/${data.id}`);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'The proposal could not be saved. Sign in and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div style={{ maxWidth: 640 }}>
        <div className="page-header">
          <div>
            <p className="page-kicker">Directory</p>
            <h1 className="page-title">Propose a club</h1>
            <p className="page-subtitle">An administrator approves it before it appears in the directory.</p>
          </div>
        </div>
        <form className="card stack" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="club-college">College</label>
            <select id="club-college" className="form-control" name="college_id" value={form.college_id} onChange={handleChange} required>
              <option value="">Select a college</option>
              {colleges.map((college) => <option key={college.id} value={college.id}>{college.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="club-name">Name</label>
            <input id="club-name" className="form-control" name="name" value={form.name} onChange={handleChange} required />
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label" htmlFor="club-short">Short name</label>
              <input id="club-short" className="form-control" name="short_name" value={form.short_name} onChange={handleChange} maxLength={30} />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="club-type">Type</label>
              <select id="club-type" className="form-control" name="club_type" value={form.club_type} onChange={handleChange}>
                <option value="departmental">Departmental</option>
                <option value="inter_departmental">Inter-department</option>
                <option value="institute_level">Institute</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="club-tagline">Tagline</label>
            <input id="club-tagline" className="form-control" name="tagline" value={form.tagline} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="club-desc">Description</label>
            <textarea id="club-desc" className="form-control" name="description" rows={4} value={form.description} onChange={handleChange} />
          </div>
          {error && <p className="form-error">{error}</p>}
          <button className="btn btn--primary" type="submit" disabled={loading || colleges.length === 0}>
            {loading ? <span className="spinner" /> : 'Submit proposal'}
          </button>
        </form>
      </div>
    </AppLayout>
  );
}
