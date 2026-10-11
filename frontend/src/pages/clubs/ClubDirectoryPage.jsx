import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import AppLayout from '../../components/layout/AppLayout';
import Icon from '../../components/common/Icon';
import { Empty, initials, washFor } from '../../components/common/Marks';
import { clubApi, institutionApi } from '../../api';
import { useAuth } from '../../contexts/AuthContext';

const CLUB_TYPE_LABELS = {
  departmental: 'Departmental',
  inter_departmental: 'Inter-department',
  institute_level: 'Institute',
};

export default function ClubDirectoryPage() {
  const { user } = useAuth();
  const [clubs, setClubs] = useState([]);
  const [colleges, setColleges] = useState([]);
  const [selectedCollege, setSelectedCollege] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    institutionApi.listColleges().then((r) => setColleges(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setFailed(false);
    const params = selectedCollege ? { college_id: selectedCollege } : {};
    clubApi.list(params)
      .then((r) => setClubs(r.data))
      .catch(() => setFailed(true))
      .finally(() => setLoading(false));
  }, [selectedCollege]);

  const filtered = clubs.filter((club) =>
    club.name.toLowerCase().includes(search.toLowerCase()) ||
    (club.description || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppLayout>
      <div className="page-header">
        <div>
          <p className="page-kicker">Directory</p>
          <h1 className="page-title">Clubs</h1>
          <p className="page-subtitle">Find a community at your college.</p>
        </div>
        <Link to={user ? '/clubs/new' : '/login'} className="btn btn--primary">
          <Icon name="plus" size={16} /> Propose a club
        </Link>
      </div>

      <div className="filters">
        <label className="search-field">
          <Icon name="search" size={16} />
          <input
            id="club-search"
            className="form-control"
            placeholder="Search by name"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search clubs"
          />
        </label>
        <select
          id="college-filter"
          className="form-control"
          style={{ maxWidth: 240 }}
          value={selectedCollege}
          onChange={(e) => setSelectedCollege(e.target.value)}
          aria-label="Filter by college"
        >
          <option value="">All colleges</option>
          {colleges.map((college) => (
            <option key={college.id} value={college.id}>{college.name}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="page-loader"><div className="spinner" /></div>
      ) : failed ? (
        <Empty title="Directory unavailable" text="The club list could not be loaded. Check that the API is running." />
      ) : filtered.length === 0 ? (
        <Empty title="No clubs match" text="Try another name, or clear the college filter." />
      ) : (
        <div className="grid-3">
          {filtered.map((club) => (
  <Link
    key={club.id}
    to={`/clubs/${club.id}`}
    aria-label={`View ${club.name} club details`}
    className="club-card-link"
  >
              <article className="card card--clickable club-card">
                <div className="club-card__cover" style={{ background: washFor(club.name) }}>
                  {initials(club.name)}
                </div>
                <h2 className="club-card__name">{club.name}</h2>
                <div className="club-card__meta">
                  <span className="badge badge--primary">{CLUB_TYPE_LABELS[club.club_type] || club.club_type}</span>
                  {club.short_name && <span className="badge badge--muted">{club.short_name}</span>}
                </div>
                {club.description && (
                  <p className="text-sm text-muted" style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {club.description}
                  </p>
                )}
              </article>
            </Link>
          ))}
        </div>
      )}
    </AppLayout>
  );
}
