import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import AppLayout from '../../components/layout/AppLayout';
import Icon from '../../components/common/Icon';
import { Empty, Monogram } from '../../components/common/Marks';
import { useAuth } from '../../contexts/AuthContext';
import { clubApi, eventApi, notificationApi } from '../../api';

export default function DashboardPage() {
  const { user } = useAuth();
  const [clubs, setClubs] = useState([]);
  const [clubCount, setClubCount] = useState(0);
  const [events, setEvents] = useState([]);
  const [eventCount, setEventCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    const jobs = [
      clubApi.list().then((r) => {
        setClubCount(r.data.length);
        setClubs(r.data.slice(0, 6));
      }),
      eventApi.list().then((r) => {
        setEventCount(r.data.length);
        setEvents(r.data.slice(0, 5));
      }),
    ];
    if (user) {
      jobs.push(
        notificationApi.list().then((r) => setNotifications(r.data.filter((n) => !n.is_read).slice(0, 5)))
      );
    }
    Promise.allSettled(jobs).then((results) => {
      setOffline(results.every((result) => result.status === 'rejected'));
      setLoading(false);
    });
  }, [user]);

  const first = user?.full_name?.split(' ')[0];
  const role = user?.global_role?.replaceAll('_', ' ') || 'Guest';
  const stats = [
    { icon: 'clubs', label: 'Active clubs', value: clubCount },
    { icon: 'calendar', label: 'Listed events', value: eventCount },
    { icon: 'bell', label: 'Unread notices', value: notifications.length },
    { icon: 'users', label: 'Your role', value: role },
  ];

  if (loading) {
    return <AppLayout><div className="page-loader"><div className="spinner" /></div></AppLayout>;
  }

  return (
    <AppLayout>
      <p className="page-kicker">Dashboard</p>
      <div className="page-header">
        <div>
          <h1 className="page-title">{first ? `Good to see you, ${first}` : 'Campus notice board'}</h1>
          <p className="page-subtitle">Clubs, events, and notices in one place.</p>
        </div>
      </div>

      {offline && (
        <p className="form-error" style={{ marginBottom: '1rem' }}>
          The API is not reachable. Start the backend on port 8000, then refresh.
        </p>
      )}

      <div className="grid-4" style={{ marginBottom: '1.4rem' }}>
        {stats.map((stat) => (
          <div key={stat.label} className="stat-card">
            <div className="stat-card__icon"><Icon name={stat.icon} /></div>
            <div className="stat-card__value">{stat.value}</div>
            <div className="stat-card__label">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="grid-2">
        <section className="card">
          <div className="card__header flex justify-between items-center">
            <div>
              <div className="card__title">Active clubs</div>
              <div className="card__subtitle">Open to students</div>
            </div>
            <Link to="/clubs" className="btn btn--secondary btn--sm">Directory</Link>
          </div>
          {clubs.length === 0 ? (
            <Empty title="No clubs yet" text="When a college approves a club, it will show up here." />
          ) : clubs.map((club) => (
            <Link key={club.id} to={`/clubs/${club.id}`} className="row-link">
              <div className="list-row">
                <Monogram name={club.name} />
                <div style={{ minWidth: 0, flex: 1 }}>
                  <div className="text-sm font-bold truncate">{club.name}</div>
                  <div className="text-xs text-muted">{club.club_type?.replaceAll('_', ' ')}</div>
                </div>
                <span className="badge badge--success">Active</span>
              </div>
            </Link>
          ))}
        </section>

        <section className="card">
          <div className="card__header flex justify-between items-center">
            <div>
              <div className="card__title">Events</div>
              <div className="card__subtitle">Public calendar</div>
            </div>
            <Link to="/events" className="btn btn--secondary btn--sm">Calendar</Link>
          </div>
          {events.length === 0 ? (
            <Empty title="No events listed" text="Club leads can publish an event from the calendar." />
          ) : events.map((ev) => {
            const date = ev.start_datetime ? new Date(ev.start_datetime) : null;
            return (
              <Link key={ev.id} to={`/events/${ev.id}`} className="row-link">
                <div className="list-row">
                  <div className="event-card__date">
                    <div className="event-card__month">{date ? date.toLocaleString('default', { month: 'short' }) : 'TBD'}</div>
                    <div className="event-card__day">{date ? date.getDate() : '--'}</div>
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div className="text-sm font-bold truncate">{ev.title}</div>
                    <div className="text-xs text-muted">{ev.venue || 'Venue to be announced'}</div>
                  </div>
                </div>
              </Link>
            );
          })}
        </section>
      </div>

      {notifications.length > 0 && (
        <section className="card" style={{ marginTop: '1rem' }}>
          <div className="card__title">Notices</div>
          {notifications.map((note) => (
            <div key={note.id} className="notice-row">
              <div>
                <div className="text-sm font-bold">{note.title}</div>
                <div className="text-xs text-muted">{note.message}</div>
              </div>
              <span className="badge badge--warning">New</span>
            </div>
          ))}
        </section>
      )}
    </AppLayout>
  );
}
