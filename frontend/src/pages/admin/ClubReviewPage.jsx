import { useEffect, useState } from 'react';
import AppLayout from '../../components/layout/AppLayout';
import Icon from '../../components/common/Icon';
import { Empty } from '../../components/common/Marks';
import { clubApi } from '../../api';

const CLUB_TYPE_LABELS = {
  departmental: 'Departmental',
  inter_departmental: 'Inter-department',
  institute_level: 'Institute',
};

export default function ClubReviewPage() {
  const [clubs, setClubs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);
  const [error, setError] = useState('');
  const [loadError, setLoadError] = useState('');

  const loadPending = async () => {
    setLoading(true);
    setFailed(false);
    setLoadError('');
    try {
      const { data } = await clubApi.pending();
      setClubs(data);
    } catch (err) {
      setFailed(true);
      const detail = err?.response?.data?.detail;
      setLoadError(typeof detail === 'string' ? detail : 'The club proposal queue could not be loaded.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPending();
  }, []);

  const reviewClub = async (clubId, action) => {
    setPendingAction({ clubId, action });
    setError('');
    try {
      if (action === 'approve') await clubApi.approve(clubId);
      else await clubApi.sendBack(clubId);
      setClubs((current) => current.filter((club) => club.id !== clubId));
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'The proposal could not be reviewed. Please try again.');
    } finally {
      setPendingAction(null);
    }
  };

  return (
    <AppLayout>
      <div className="page-header">
        <div>
          <p className="page-kicker">Admin</p>
          <h1 className="page-title">Club proposals</h1>
          <p className="page-subtitle">Review new clubs before they appear in the directory.</p>
        </div>
        {!loading && !failed && <span className="badge badge--warning">{clubs.length} awaiting review</span>}
      </div>

      {error && <p className="form-error" role="alert" style={{ marginBottom: '1rem' }}>{error}</p>}
      {loading ? (
        <div className="page-loader"><div className="spinner" /></div>
      ) : failed ? (
        <div className="stack">
          <Empty title="Queue unavailable" text={loadError} />
          <button className="btn btn--secondary" type="button" onClick={loadPending}>Try again</button>
        </div>
      ) : clubs.length === 0 ? (
        <Empty title="All caught up" text="New club proposals will appear here for review." />
      ) : (
        <div className="review-queue">
          {clubs.map((club) => (
            <article className="card review-card" key={club.id}>
              <div className="review-card__content">
                <div className="flex gap-1 items-center" style={{ marginBottom: '0.5rem' }}>
                  <span className="badge badge--primary">{CLUB_TYPE_LABELS[club.club_type] || club.club_type}</span>
                  {club.short_name && <span className="badge badge--muted">{club.short_name}</span>}
                </div>
                <h2>{club.name}</h2>
                {club.tagline && <p className="text-sm" style={{ marginTop: '0.35rem' }}>{club.tagline}</p>}
                <p className="text-sm text-muted" style={{ marginTop: '0.5rem' }}>
                  {club.description || 'No description provided.'}
                </p>
              </div>
              <div className="review-card__actions">
                <button
                  className="btn btn--primary"
                  type="button"
                  onClick={() => reviewClub(club.id, 'approve')}
                  disabled={pendingAction !== null}
                >
                  {pendingAction?.clubId === club.id && pendingAction.action === 'approve'
                    ? <span className="spinner" />
                    : <Icon name="check" size={16} />}
                  Approve
                </button>
                <button
                  className="btn btn--danger"
                  type="button"
                  onClick={() => reviewClub(club.id, 'send-back')}
                  disabled={pendingAction !== null}
                >
                  {pendingAction?.clubId === club.id && pendingAction.action === 'send-back' && <span className="spinner" />}
                  Send back for changes
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </AppLayout>
  );
}
