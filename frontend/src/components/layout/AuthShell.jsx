import { Mark } from '../common/Icon';

export default function AuthShell({ title, subtitle, children }) {
  return (
    <div className="auth-page">
      <aside className="auth-aside">
        <div>
          <Mark size={36} />
          <p className="auth-aside__kicker">LTCE campus</p>
          <h1>One record for every club.</h1>
          <p>A college registers itself. Each club keeps its history. Students find a room to join.</p>
        </div>
        <p className="auth-aside__foot">ClubHub, an open record for campus life.</p>
      </aside>
      <section className="auth-card">
        <h2>{title}</h2>
        <p className="auth-card__subtitle">{subtitle}</p>
        {children}
      </section>
    </div>
  );
}
