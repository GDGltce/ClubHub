import { useEffect, useState } from 'react';
import AppLayout from '../../components/layout/AppLayout';
import Icon from '../../components/common/Icon';
import { Empty, Monogram } from '../../components/common/Marks';
import { userApi } from '../../api';
import { useAuth } from '../../contexts/AuthContext';

const ROLE_LABELS = {
  platform_admin: 'Platform admin',
  faculty_coordinator: 'Faculty coordinator',
  student: 'Student',
};

const ROLE_BADGES = {
  platform_admin: 'badge--danger',
  faculty_coordinator: 'badge--warning',
  student: 'badge--muted',
};

export default function UserManagementPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [actionError, setActionError] = useState('');
  const [pendingAction, setPendingAction] = useState(null);

  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const loadUsers = async () => {
    setLoading(true);
    setLoadError('');
    try {
      const { data } = await userApi.list();
      setUsers(data);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setLoadError(typeof detail === 'string' ? detail : 'User accounts could not be loaded.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleToggleStatus = async (user) => {
    setPendingAction({ userId: user.id, type: 'status' });
    setActionError('');
    try {
      const { data } = await userApi.update(user.id, { is_active: !user.is_active });
      setUsers((prev) => prev.map((u) => (u.id === user.id ? data : u)));
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setActionError(typeof detail === 'string' ? detail : 'Failed to update account status.');
    } finally {
      setPendingAction(null);
    }
  };

  const handleRoleChange = async (user, newRole) => {
    if (user.global_role === newRole) return;
    setPendingAction({ userId: user.id, type: 'role' });
    setActionError('');
    try {
      const { data } = await userApi.update(user.id, { global_role: newRole });
      setUsers((prev) => prev.map((u) => (u.id === user.id ? data : u)));
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setActionError(typeof detail === 'string' ? detail : 'Failed to update user role.');
    } finally {
      setPendingAction(null);
    }
  };

  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      !search ||
      u.full_name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase());
    const matchesRole = !roleFilter || u.global_role === roleFilter;
    const matchesStatus =
      !statusFilter ||
      (statusFilter === 'active' && u.is_active) ||
      (statusFilter === 'inactive' && !u.is_active);
    return matchesSearch && matchesRole && matchesStatus;
  });

  const activeCount = users.filter((u) => u.is_active).length;

  return (
    <AppLayout>
      <div className="page-header">
        <div>
          <p className="page-kicker">Admin</p>
          <h1 className="page-title">Users & Accounts</h1>
          <p className="page-subtitle">Review campus accounts, assigned roles, and activity status.</p>
        </div>
        {!loading && !loadError && (
          <div className="flex gap-1">
            <span className="badge badge--primary">{users.length} total</span>
            <span className="badge badge--success">{activeCount} active</span>
          </div>
        )}
      </div>

      {actionError && (
        <p className="form-error" role="alert" style={{ marginBottom: '1rem' }}>
          {actionError}
        </p>
      )}

      <div className="filters">
        <label className="search-field">
          <Icon name="search" size={16} />
          <input
            id="user-search"
            className="form-control"
            type="search"
            placeholder="Search by name or email…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </label>

        <select
          id="role-filter"
          className="form-control"
          style={{ maxWidth: '200px' }}
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
        >
          <option value="">All roles</option>
          <option value="student">Student</option>
          <option value="faculty_coordinator">Faculty coordinator</option>
          <option value="platform_admin">Platform admin</option>
        </select>

        <select
          id="status-filter"
          className="form-control"
          style={{ maxWidth: '180px' }}
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All statuses</option>
          <option value="active">Active only</option>
          <option value="inactive">Inactive only</option>
        </select>
      </div>

      {loading ? (
        <div className="page-loader">
          <div className="spinner" />
        </div>
      ) : loadError ? (
        <div className="stack">
          <Empty title="Users unavailable" text={loadError} />
          <button className="btn btn--secondary" type="button" onClick={loadUsers}>
            Try again
          </button>
        </div>
      ) : filteredUsers.length === 0 ? (
        <Empty
          title="No accounts found"
          text={
            users.length === 0
              ? 'No user accounts are registered in the platform yet.'
              : 'No user accounts match the selected filters.'
          }
        />
      ) : (
        <div className="review-queue">
          {filteredUsers.map((item) => {
            const isSelf = item.id === currentUser?.id;
            const isPendingStatus =
              pendingAction?.userId === item.id && pendingAction.type === 'status';
            const isPendingRole =
              pendingAction?.userId === item.id && pendingAction.type === 'role';

            return (
              <article className="card user-card" key={item.id}>
                <div className="user-card__info">
                  <Monogram name={item.full_name} size={42} />
                  <div className="user-card__meta">
                    <div className="flex gap-1 items-center" style={{ flexWrap: 'wrap' }}>
                      <h2 style={{ fontSize: '1.15rem' }}>{item.full_name}</h2>
                      {isSelf && <span className="badge badge--primary">You</span>}
                    </div>
                    <p className="text-sm text-muted" style={{ marginTop: '0.15rem' }}>
                      {item.email}
                    </p>
                    <div className="flex gap-1 items-center" style={{ marginTop: '0.45rem' }}>
                      <span className={`badge ${ROLE_BADGES[item.global_role] || 'badge--muted'}`}>
                        {ROLE_LABELS[item.global_role] || item.global_role}
                      </span>
                      <span
                        className={`badge ${item.is_active ? 'badge--success' : 'badge--danger'}`}
                      >
                        {item.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="user-card__actions">
                  <label htmlFor={`role-select-${item.id}`} className="sr-only" style={{ display: 'none' }}>
                    Role for {item.full_name}
                  </label>
                  <select
                    id={`role-select-${item.id}`}
                    aria-label={`Role for ${item.full_name}`}
                    className="form-control"
                    style={{ fontSize: '0.85rem', padding: '0.4rem 0.5rem', width: 'auto' }}
                    value={item.global_role}
                    onChange={(e) => handleRoleChange(item, e.target.value)}
                    disabled={isSelf || isPendingRole}
                  >
                    <option value="student">Student</option>
                    <option value="faculty_coordinator">Faculty coordinator</option>
                    <option value="platform_admin">Platform admin</option>
                  </select>

                  <button
                    className={`btn btn--sm ${item.is_active ? 'btn--secondary' : 'btn--primary'}`}
                    type="button"
                    onClick={() => handleToggleStatus(item)}
                    disabled={isSelf || isPendingStatus}
                    title={isSelf ? 'Cannot deactivate your own account' : undefined}
                  >
                    {isPendingStatus && <span className="spinner" />}
                    {item.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </AppLayout>
  );
}
