import { useEffect, useState } from 'react';
import AppLayout from '../../components/layout/AppLayout';
import { institutionApi } from '../../api';

export default function InstitutionAdminPage() {
  const [colleges, setColleges] = useState([]);
  const [college, setCollege] = useState({
    name: '',
    short_name: '',
    university: '',
    city: '',
    state: '',
    website: '',
  });
  const [department, setDepartment] = useState({
    college_id: '',
    name: '',
    short_name: '',
  });
  const [collegeMsg, setCollegeMsg] = useState(null);
  const [deptMsg, setDeptMsg] = useState(null);
  const [collegeLoading, setCollegeLoading] = useState(false);
  const [deptLoading, setDeptLoading] = useState(false);

  useEffect(() => {
    institutionApi.listColleges()
      .then((r) => setColleges(r.data))
      .catch(() => {});
  }, []);

  const handleChange = (setter) => (e) =>
    setter((current) => ({ ...current, [e.target.name]: e.target.value }));

  const detail = (err, fallback) => {
    const d = err?.response?.data?.detail;
    return typeof d === 'string' ? d : fallback;
  };

  const nullable = (value) => value || null;

  const handleCollege = async (e) => {
    e.preventDefault();
    setCollegeMsg(null);
    setCollegeLoading(true);
    try {
      const payload = {
        name: college.name,
        short_name: nullable(college.short_name),
        university: nullable(college.university),
        city: nullable(college.city),
        state: nullable(college.state),
        website: nullable(college.website),
      };
      const { data } = await institutionApi.createCollege(payload);
      setColleges((current) => [...current, data]);
      setCollege({ name: '', short_name: '', university: '', city: '', state: '', website: '' });
      setDepartment((current) => ({ ...current, college_id: current.college_id || data.id }));
      setCollegeMsg({ ok: true, text: `${data.name} registered.` });
    } catch (err) {
      setCollegeMsg({ ok: false, text: detail(err, 'The college could not be registered.') });
    } finally {
      setCollegeLoading(false);
    }
  };

  const handleDepartment = async (e) => {
    e.preventDefault();
    setDeptMsg(null);
    setDeptLoading(true);
    try {
      await institutionApi.createDepartment(department.college_id, {
        name: department.name,
        short_name: nullable(department.short_name),
      });
      setDepartment((current) => ({ ...current, name: '', short_name: '' }));
      setDeptMsg({ ok: true, text: 'Department added.' });
    } catch (err) {
      setDeptMsg({ ok: false, text: detail(err, 'The department could not be added.') });
    } finally {
      setDeptLoading(false);
    }
  };

  return (
    <AppLayout>
      <div style={{ maxWidth: 640 }}>
        <div className="page-header">
          <div>
            <p className="page-kicker">Admin</p>
            <h1 className="page-title">Institutions</h1>
            <p className="page-subtitle">Register a college and its departments.</p>
          </div>
        </div>

        <form className="card stack" onSubmit={handleCollege}>
          <h2 className="card__title">Register college</h2>
          <div className="form-group">
            <label className="form-label" htmlFor="college-name">Name</label>
            <input id="college-name" className="form-control" name="name" value={college.name} onChange={handleChange(setCollege)} required />
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label" htmlFor="college-short">Short name</label>
              <input id="college-short" className="form-control" name="short_name" value={college.short_name} onChange={handleChange(setCollege)} maxLength={20} />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="college-university">University</label>
              <input id="college-university" className="form-control" name="university" value={college.university} onChange={handleChange(setCollege)} />
            </div>
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label" htmlFor="college-city">City</label>
              <input id="college-city" className="form-control" name="city" value={college.city} onChange={handleChange(setCollege)} />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="college-state">State</label>
              <input id="college-state" className="form-control" name="state" value={college.state} onChange={handleChange(setCollege)} />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="college-website">Website</label>
            <input id="college-website" className="form-control" name="website" value={college.website} onChange={handleChange(setCollege)} type="url" />
          </div>
          {collegeMsg && <p className={`form-note ${collegeMsg.ok ? 'form-note--ok' : 'form-note--bad'}`}>{collegeMsg.text}</p>}
          <button className="btn btn--primary" type="submit" disabled={collegeLoading}>
            {collegeLoading ? <span className="spinner" /> : 'Register college'}
          </button>
        </form>

        <form className="card stack" style={{ marginTop: '1rem' }} onSubmit={handleDepartment}>
          <h2 className="card__title">Add department</h2>
          <div className="form-group">
            <label className="form-label" htmlFor="dept-college">College</label>
            <select id="dept-college" className="form-control" name="college_id" value={department.college_id} onChange={handleChange(setDepartment)} required>
              <option value="">Select a college</option>
              {colleges.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label" htmlFor="dept-name">Name</label>
              <input id="dept-name" className="form-control" name="name" value={department.name} onChange={handleChange(setDepartment)} required />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="dept-short">Short name</label>
              <input id="dept-short" className="form-control" name="short_name" value={department.short_name} onChange={handleChange(setDepartment)} maxLength={20} />
            </div>
          </div>
          {deptMsg && <p className={`form-note ${deptMsg.ok ? 'form-note--ok' : 'form-note--bad'}`}>{deptMsg.text}</p>}
          <button className="btn btn--primary" type="submit" disabled={deptLoading || colleges.length === 0}>
            {deptLoading ? <span className="spinner" /> : 'Add department'}
          </button>
        </form>
      </div>
    </AppLayout>
  );
}
