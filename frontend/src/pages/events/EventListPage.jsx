import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import AppLayout from '../../components/layout/AppLayout';
import Icon from '../../components/common/Icon';
import { Empty } from '../../components/common/Marks';
import { clubApi, eventApi } from '../../api';
import { useAuth } from '../../contexts/AuthContext';

const STAGES = ['idea', 'permission', 'funds', 'planning', 'promotion', 'pre_event', 'execution', 'post_event', 'archived'];
const STAGE_LABELS = {
  idea: 'Idea',
  permission: 'Permission',
  funds: 'Funds',
  planning: 'Planning',
  promotion: 'Promotion',
  pre_event: 'Pre-event',
  execution: 'Execution',
  post_event: 'Post-event',
  archived: 'Archived',
};

const STAGE_COLORS = {
  idea: 'badge--muted',
  permission: 'badge--warning',
  funds: 'badge--warning',
  planning: 'badge--primary',
  promotion: 'badge--primary',
  pre_event: 'badge--info',
  execution: 'badge--success',
  post_event: 'badge--success',
  archived: 'badge--muted',
};

export default function EventListPage() {
  const { user } = useAuth();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [clubs, setClubs] = useState([]);
  const [clubId, setClubId] = useState('');
  const [stage, setStage] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const hasFilters = Boolean(clubId || stage || dateFrom || dateTo);

  useEffect(() => {
    clubApi.list().then((r) => setClubs(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setFailed(false);
    const params = {};
    if (clubId) params.club_id = clubId;
    if (stage) params.stage = stage;
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    eventApi.list(params)
      .then((r) => setEvents(r.data))
      .catch(() => setFailed(true))
      .finally(() => setLoading(false));
  }, [clubId, stage, dateFrom, dateTo]);

  return (
    <AppLayout>
      <div className="page-header">
        <div>
          <p className="page-kicker">Calendar</p>
          <h1 className="page-title">Events</h1>
          <p className="page-subtitle">Public events across clubs.</p>
        </div>
        <Link to={user ? '/events/new' : '/login'} className="btn btn--primary">
          <Icon name="plus" size={16} /> Create event
        </Link>
      </div>

      <div className="card filters-card">
        <div className="filters-card__tags">
          <button
            type="button"
            className={`badge ${stage ? STAGE_COLORS[stage] : 'badge--muted'}`}
            onClick={() => setStage('')}
          >
            {stage ? STAGE_LABELS[stage] : 'All stages'}
          </button>
          {stage && STAGES.map((s) => (
            <button
              key={s}
              type="button"
              className={`badge ${STAGE_COLORS[s]}`}
              onClick={() => setStage(s)}
            >
              {STAGE_LABELS[s]}
            </button>
          ))}
        </div>
        <div className="filters">
          <select
            className="form-control"
            value={clubId}
            onChange={(e) => setClubId(e.target.value)}
            aria-label="Filter by club"
          >
            <option value="">All clubs</option>
            {clubs.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <input
            type="date"
            className="form-control"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            aria-label="From date"
          />
          <input
            type="date"
            className="form-control"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            aria-label="To date"
          />
          {hasFilters && (
            <button
              type="button"
              className="btn"
              onClick={() => { setStage(''); setClubId(''); setDateFrom(''); setDateTo(''); }}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="page-loader"><div className="spinner" /></div>
      ) : failed ? (
        <Empty title="Calendar unavailable" text="Events could not be loaded. Check that the API is running." />
      ) : events.length === 0 ? (
        <Empty
          title={hasFilters ? 'No events match' : 'No events yet'}
          text={hasFilters ? 'Try another club, stage, or date.' : 'The first published event will appear here.'}
        />
      ) : (
        <div className="stack">
          {events.map((ev) => {
            const date = ev.start_datetime ? new Date(ev.start_datetime) : null;
            return (
              <Link key={ev.id} to={`/events/${ev.id}`}>
                <article className="card card--clickable event-card">
                  <div className="event-card__date">
                    <div className="event-card__month">{date ? date.toLocaleString('default', { month: 'short' }) : 'TBD'}</div>
                    <div className="event-card__day">{date ? date.getDate() : '--'}</div>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="flex justify-between items-center gap-2">
                      <span className="font-bold truncate">{ev.title}</span>
                      <span className={`badge ${STAGE_COLORS[ev.stage] || 'badge--muted'}`}>{ev.stage?.replaceAll('_', ' ')}</span>
                    </div>
                    <div className="text-xs text-muted mt-1">{ev.venue || 'Venue to be announced'}{ev.audience ? ` · ${ev.audience}` : ''}</div>
                  </div>
                </article>
              </Link>
            );
          })}
        </div>
      )}
    </AppLayout>
  );
}
