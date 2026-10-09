import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Mark } from '../common/Icon';
import Icon from '../common/Icon';

export default function Navbar({ onMenu }) {
  const { user, logout, loading } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const role = user?.global_role?.replaceAll('_', ' ');

  return (
    <nav className="navbar">
      <div className="flex items-center gap-2">
        <button className="navbar__menu" type="button" aria-label="Open menu" onClick={onMenu}>
          <Icon name="menu" />
        </button>
        <Link to="/dashboard" className="navbar__brand">
          <Mark size={26} />
          <span>
            <span className="navbar__logo">ClubHub</span>
            <span className="navbar__kicker"> campus record</span>
          </span>
        </Link>
      </div>
      <div className="navbar__actions">
        {loading ? null : user ? (
          <>
            <span className="text-sm">{user.full_name}</span>
            {role && <span className="badge badge--primary">{role}</span>}
            <button className="btn btn--secondary btn--sm" onClick={handleLogout}>
              <Icon name="logout" size={15} /> Sign out
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="btn btn--secondary btn--sm">Sign in</Link>
            <Link to="/register" className="btn btn--primary btn--sm">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
