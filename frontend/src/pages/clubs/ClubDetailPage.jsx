import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import AppLayout from '../../components/layout/AppLayout';
import Icon from '../../components/common/Icon';
import { Empty, initials, washFor } from '../../components/common/Marks';
import { clubApi, membershipApi, eventApi } from '../../api';
import { useAuth } from '../../contexts/AuthContext';
import JoinRequestsList from './JoinRequestsList';

const STAGES = ['idea', 'permission', 'funds', 'planning', 'promotion', 'pre_event', 'execution', 'post_event', 'archived'];

export default function ClubDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [club, setClub] = useState(null);
  const [events, setEvents] = useState([]);
  const [joinNote, setJoinNote] = useState('');
  const [joining, setJoining] = useState(false);
  const [joinState, setJoinState] = useState(null);

  useEffect(() => {
    clubApi.get(id).then((r) => setClub(r.data)).catch(() => navigate('/clubs'));
    eventApi.list({ club_id: id }).then((r) => setEvents(r.data)).catch(() => {});
  }, [id, navigate]);

  const handleJoin = async () => {
    if (!user) return navigate('/login');
    setJoining(true);
    setJoinState(null);
    try {
      await membershipApi.submitJoinRequest({ club_id: id, motivation: joinNote });
      setJoinState({ ok: true, text: 'Request sent. A club lead will review it.' });
    } catch (err) {
      setJoinState({ ok: false, text: err?.response?.data?.detail || 'The request could not be sent.' });
    } finally {
      setJoining(false);
    }
  };

  if (!club) return <AppLayout><div className="page-loader"><div className="spinner" /></div></AppLayout>;

  const isClubLead = user && club && user.id === club.lead_id;
  // console.log("Full Club Data:", club);

  return (
    <AppLayout>
      <div className="club-hero" style={{ background: washFor(club.name) }}>
        <p className="page-kicker" style={{ color: '#f3efe6' }}>{initials(club.name)}</p>
        <h1>{club.name}</h1>
        <div className="flex gap-1" style={{ marginTop: '0.55rem' }}>
          <span className="badge" style={{ color: '#faf7f1', borderColor: 'rgba(250,247,241,0.5)' }}>{club.status}</span>
          <span className="badge" style={{ color: '#faf7f1', borderColor: 'rgba(250,247,241,0.5)' }}>{club.club_type?.replaceAll('_', ' ')}</span>
          {club.short_name && <span className="badge" style={{ color: '#faf7f1', borderColor: 'rgba(250,247,241,0.5)' }}>{club.short_name}</span>}
        </div>
      </div>

      {club.status === 'pending' && (
        <p className="text-sm" style={{ marginBottom: '1rem' }}>
          This proposal is waiting for an administrator to approve it. It will not appear in the directory until then.
        </p>
      )}

      <div className="grid-2">
        <div className="stack">
          <section className="card">
            <h2 className="card__title">About</h2>
            <p className="text-sm text-muted mt-1">{club.description || 'No description yet.'}</p>
            {club.tagline && <p className="text-sm mt-1" style={{ fontFamily: 'var(--font-display)' }}>{club.tagline}</p>}
          </section>

          {isClubLead && <JoinRequestsList clubId={club.id} />}

          {user && user.global_role === 'student' && club.status === 'active' && !isClubLead && (
            <section className="card">
              <h2 className="card__title">Request to join</h2>
              <div className="form-group" style={{ marginTop: '0.75rem' }}>
                <label className="form-label" htmlFor="join-note">Why do you want to join?</label>
                <textarea id="join-note" className="form-control" rows={3} placeholder="A short note for the club lead" value={joinNote} onChange={(e) => setJoinNote(e.target.value)} />
              </div>
              {joinState ? (
                <p className={`form-note ${joinState.ok ? 'form-note--ok' : 'form-note--bad'}`}>{joinState.text}</p>
              ) : (
                <button id={`join-club-${id}`} className="btn btn--primary" style={{ marginTop: '0.75rem' }} onClick={handleJoin} disabled={joining}>
                  {joining ? <span className="spinner" /> : 'Send request'}
                </button>
              )}
            </section>
          )}
        </div>

        <section className="card">
          <div className="card__header flex justify-between items-center">
            <h2 className="card__title">Events</h2>
            {user && <Link to={`/events/new?club_id=${id}`} className="btn btn--primary btn--sm"><Icon name="plus" size={14} /> Event</Link>}
          </div>
          {events.length === 0 ? (
            <Empty title="No events yet" text="Published events for this club will be listed here." />
          ) : events.map((ev) => {
            const stageIdx = Math.max(STAGES.indexOf(ev.stage), 0);
            return (
              <Link key={ev.id} to={`/events/${ev.id}`} className="row-link">
                <div className="list-row" style={{ display: 'block' }}>
                  <div className="flex justify-between items-center">
                    <div className="text-sm font-bold">{ev.title}</div>
                    <span className="badge badge--primary">{ev.stage?.replaceAll('_', ' ')}</span>
                  </div>
                  <div className="meter"><span style={{ width: `${((stageIdx + 1) / STAGES.length) * 100}%` }} /></div>
                  <div className="text-xs text-muted" style={{ marginTop: '0.3rem' }}>{stageIdx + 1} of {STAGES.length} stages</div>
                </div>
              </Link>
            );
          })}
        </section>
      </div>
    </AppLayout>
  );
}