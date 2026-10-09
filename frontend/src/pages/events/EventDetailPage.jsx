import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AppLayout from '../../components/layout/AppLayout';
import Icon from '../../components/common/Icon';
import { eventApi } from '../../api';
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

export default function EventDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [advancing, setAdvancing] = useState(false);
  const [note, setNote] = useState('');
  const [msg, setMsg] = useState(null);

  useEffect(() => {
    eventApi.get(id).then((r) => setEvent(r.data)).catch(() => navigate('/events'));
  }, [id, navigate]);

  const handleAdvance = async () => {
    setAdvancing(true);
    setMsg(null);
    try {
      const { data } = await eventApi.advanceStage(id, { notes: note });
      setEvent(data);
      setNote('');
      setMsg({ ok: true, text: 'Stage updated.' });
    } catch (err) {
      setMsg({ ok: false, text: err?.response?.data?.detail || 'The stage could not be updated.' });
    } finally {
      setAdvancing(false);
    }
  };

  if (!event) return <AppLayout><div className="page-loader"><div className="spinner" /></div></AppLayout>;

  const currentIdx = STAGES.indexOf(event.stage);
  const date = event.start_datetime ? new Date(event.start_datetime) : null;
  const canAdvance = user && !event.is_locked && currentIdx >= 0 && currentIdx < STAGES.length - 1;
  const facts = [
    { label: 'Venue', value: event.venue || 'To be announced' },
    { label: 'Date', value: date ? date.toLocaleDateString() : 'To be announced' },
    { label: 'Expected turnout', value: event.expected_turnout || 'Not set' },
    { label: 'Audience', value: event.audience || 'Open' },
  ];

  return (
    <AppLayout>
      <div className="card" style={{ marginBottom: '1.1rem', padding: '0.8rem 0.9rem 0.4rem' }}>
        <div className="stepper">
          {STAGES.map((stage, index) => (
            <div key={stage} className={`step ${index < currentIdx ? 'step--done' : index === currentIdx ? 'step--active' : ''}`}>
              {STAGE_LABELS[stage]}
            </div>
          ))}
        </div>
      </div>

      <div className="grid-2">
        <div className="stack">
          <section className="card">
            <div className="flex gap-1" style={{ marginBottom: '0.55rem', flexWrap: 'wrap' }}>
              <span className="badge badge--primary">{event.stage?.replaceAll('_', ' ')}</span>
              <span className="badge badge--muted">{event.visibility?.replaceAll('_', ' ')}</span>
              {event.is_locked && <span className="badge badge--danger">Locked</span>}
            </div>
            <h1 className="page-title" style={{ fontSize: '1.8rem' }}>{event.title}</h1>
            {event.description && <p className="text-sm text-muted mt-1">{event.description}</p>}
            <div className="divider" />
            <dl className="fact-grid">
              {facts.map((fact) => (
                <div key={fact.label}>
                  <dt>{fact.label}</dt>
                  <dd>{fact.value}</dd>
                </div>
              ))}
            </dl>
            {event.registration_link && (
              <a href={event.registration_link} target="_blank" rel="noreferrer" className="btn btn--primary" style={{ marginTop: '1rem' }}>
                Registration form
              </a>
            )}
          </section>
          {event.goal && (
            <section className="card">
              <h2 className="card__title">Goal</h2>
              <p className="text-sm text-muted mt-1">{event.goal}</p>
            </section>
          )}
          {(event.feedback_summary || event.lessons_learned) && (
            <section className="card">
              <h2 className="card__title">After the event</h2>
              {event.feedback_summary && <p className="text-sm text-muted mt-1">{event.feedback_summary}</p>}
              {event.lessons_learned && <p className="text-sm mt-1">{event.lessons_learned}</p>}
            </section>
          )}
        </div>

        <div className="stack">
          {canAdvance && (
            <section className="card">
              <h2 className="card__title">Advance stage</h2>
              <p className="text-sm text-muted mt-1">Next: {STAGE_LABELS[STAGES[currentIdx + 1]]}</p>
              <div className="form-group" style={{ marginTop: '0.75rem' }}>
                <label className="form-label" htmlFor="stage-note">Notes</label>
                <textarea id="stage-note" className="form-control" rows={3} value={note} onChange={(e) => setNote(e.target.value)} placeholder="Optional note for the record" />
              </div>
              {msg && <p className={`form-note ${msg.ok ? 'form-note--ok' : 'form-note--bad'}`}>{msg.text}</p>}
              <button id={`advance-stage-${id}`} className="btn btn--primary" style={{ marginTop: '0.75rem' }} onClick={handleAdvance} disabled={advancing}>
                {advancing ? <span className="spinner" /> : 'Move forward'}
              </button>
            </section>
          )}
          <section className="card">
            <h2 className="card__title">Progress</h2>
            <div className="stack" style={{ marginTop: '0.7rem', gap: '0.4rem' }}>
              {STAGES.map((stage, index) => {
                const state = index < currentIdx ? 'done' : index === currentIdx ? 'now' : '';
                return (
                  <div key={stage} className={`progress-line${state ? ` progress-line--${state}` : ''}`}>
                    <Icon name={index < currentIdx ? 'check' : 'clubs'} size={14} />
                    <span>{STAGE_LABELS[stage]}</span>
                  </div>
                );
              })}
            </div>
          </section>
        </div>
      </div>
    </AppLayout>
  );
}
