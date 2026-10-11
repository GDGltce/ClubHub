import { useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Icon from '../common/Icon';

const NAV_ITEMS = [
  { label: 'Dashboard', icon: 'home', path: '/dashboard', section: 'Main' },
  { label: 'Clubs', icon: 'clubs', path: '/clubs', section: 'Main' },
  { label: 'Events', icon: 'calendar', path: '/events', section: 'Main' },
  { label: 'Meetings', icon: 'chat', path: '/meetings', section: 'Club' },
  { label: 'Documents', icon: 'file', path: '/documents', section: 'Club' },
];

const ADMIN_ITEMS = [
  { label: 'Institutions', icon: 'building', path: '/admin/institutions', section: 'Admin' },
  { label: 'Users', icon: 'users', path: '/admin/users', section: 'Admin' },
];

export default function Sidebar({ open, onNavigate }) {
  const { pathname } = useLocation();
  const { user } = useAuth();

  const sections = {};
  const allItems = [...NAV_ITEMS, ...(user?.global_role === 'platform_admin' ? ADMIN_ITEMS : [])];
  allItems.forEach((item) => {
    if (!sections[item.section]) sections[item.section] = [];
    sections[item.section].push(item);
  });

  const active = (path) => pathname === path || (path !== '/dashboard' && pathname.startsWith(path));

  return (
    <aside
  id="sidebar-navigation"
  className={`sidebar${open ? ' sidebar--open' : ''}`}
  aria-label="Main navigation"
  aria-hidden={undefined}
>
      {Object.entries(sections).map(([section, items]) => (
        <div key={section}>
          <div className="sidebar__section-label">{section}</div>
          {items.map((item) => (
            <Link
  key={item.path}
  to={item.path}
  onClick={onNavigate}
  aria-current={active(item.path) ? 'page' : undefined}
  className={`sidebar__item${active(item.path) ? ' sidebar__item--active' : ''}`}
>
              <Icon name={item.icon} size={16} />
              {item.label}
            </Link>
          ))}
        </div>
      ))}
    </aside>
  );
}
