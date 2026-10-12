import { useEffect, useState } from 'react';
import { membershipApi } from '../../api';

export default function JoinRequestsList({ clubId }) {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    setLoading(true);
    membershipApi.getJoinRequests(clubId)
      .then((r) => {
        const pending = r.data.filter((req) => req.status === 'pending');
        setRequests(pending);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [clubId]);

  const handleReview = (id, status) => {
    membershipApi.reviewRequest(id, { status })
      .then(() => setRequests((prev) => prev.filter((req) => req.id !== id)))
      .catch(() => alert(`Failed to mark request as ${status}.`));
  };

  if (loading) return <div className="spinner" />;
  if (error) return <p className="text-sm text-muted">Failed to load join requests.</p>;
  if (requests.length === 0) return null;

  return (
    <div className="stack" style={{ marginTop: '2rem' }}>
      <h3 className="font-bold">Pending Join Requests ({requests.length})</h3>
      <div className="stack">
        {requests.map((req) => (
          <article key={req.id} className="card flex justify-between items-center gap-4">
            <div style={{ flex: 1, minWidth: 0 }}>
              <p className="font-bold truncate">
                {req.user?.full_name || req.user?.email || `User #${req.user_id}`}
              </p>
              <p className="text-sm text-muted" style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {req.motivation || 'No motivation provided.'}
              </p>
            </div>
            <div className="flex gap-2">
              <button className="btn btn--primary" style={{ backgroundColor: '#10b981', borderColor: '#10b981' }} onClick={() => handleReview(req.id, 'approved')}>
                Approve
              </button>
              <button className="btn" style={{ color: '#ef4444', borderColor: '#ef4444' }} onClick={() => handleReview(req.id, 'rejected')}>
                Reject
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}