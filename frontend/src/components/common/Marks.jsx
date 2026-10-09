import Icon from '../common/Icon';

const WASHES = ['#3d4f3a', '#8c3a2f', '#2c3a4f', '#6b5428'];

export function washFor(name = '') {
  const code = name.charCodeAt(0) || 0;
  return WASHES[code % WASHES.length];
}

export function initials(name = '') {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return 'CH';
  return parts.slice(0, 2).map((part) => part[0]).join('').toUpperCase();
}

export function Monogram({ name, size = 36 }) {
  return (
    <span className="monogram" style={{ width: size, height: size, color: washFor(name) }}>
      {initials(name)}
    </span>
  );
}

export function Empty({ title, text }) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  );
}

export function StageMark({ state }) {
  const name = state === 'done' ? 'check' : 'clubs';
  return <Icon name={name} size={14} />;
}
