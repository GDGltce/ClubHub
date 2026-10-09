import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import AppLayout from '../../components/layout/AppLayout';
import Icon from '../../components/common/Icon';
import { Empty } from '../../components/common/Marks';
import { eventApi } from '../../api';
import { useAuth } from '../../contexts/AuthContext';

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

  useEffect(() => {
    eventApi.list()
      .then((r) => setEvents(r.data))
      .catch(() => setFailed(true))
      .finally(() => setLoading(false));
  }, []);

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

      {loading ? (
        <div className="page-loader"><div className="spinner" /></div>
      ) : failed ? (
        <Empty title="Calendar unavailable" text="Events could not be loaded. Check that the API is running." />
      ) : events.length === 0 ? (
        <Empty title="No events yet" text="The first published event will appear here." />
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
