import { createBrowserRouter, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AppLayout from '../components/layout/AppLayout';

// Pages
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';
import DashboardPage from '../pages/dashboard/DashboardPage';
import ClubDirectoryPage from '../pages/clubs/ClubDirectoryPage';
import ClubDetailPage from '../pages/clubs/ClubDetailPage';
import EventListPage from '../pages/events/EventListPage';
import EventDetailPage from '../pages/events/EventDetailPage';
import EventCreatePage from '../pages/events/EventCreatePage';
import ClubCreatePage from '../pages/clubs/ClubCreatePage';

// Simple Auth Guard
function Placeholder({ kicker, title, text }) {
  return (
    <AppLayout>
      <p className="page-kicker">{kicker}</p>
      <div className="page-header">
        <div>
          <h1 className="page-title">{title}</h1>
          <p className="page-subtitle">{text}</p>
        </div>
      </div>
    </AppLayout>
  );
}

const RequireAuth = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <AppLayout><div className="page-loader"><div className="spinner"/></div></AppLayout>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/dashboard',
    element: <DashboardPage />,
  },
  // Clubs
  {
    path: '/clubs',
    element: <ClubDirectoryPage />,
  },
  {
    path: '/clubs/new',
    element: <RequireAuth><ClubCreatePage /></RequireAuth>,
  },
  {
    path: '/clubs/:id',
    element: <ClubDetailPage />,
  },
  // Events
  {
    path: '/events',
    element: <EventListPage />,
  },
  {
    path: '/events/new',
    element: <RequireAuth><EventCreatePage /></RequireAuth>,
  },
  {
    path: '/events/:id',
    element: <EventDetailPage />,
  },
  // Fallback routes for undeveloped pages
  {
    path: '/meetings',
    element: <Placeholder kicker="Club" title="Meetings" text="Minutes and agendas will live here. The API exists; the page is still being built." />,
  },
  {
    path: '/documents',
    element: <Placeholder kicker="Club" title="Document vault" text="Proposals, budgets, and approvals will be filed here." />,
  },
  {
    path: '/admin/institutions',
    element: <Placeholder kicker="Admin" title="Institutions" text="College and department registration is not in the interface yet." />,
  },
  {
    path: '/admin/users',
    element: <Placeholder kicker="Admin" title="Users" text="Account review for the campus will be added here." />,
  },
  {
    path: '*',
    element: <Placeholder kicker="404" title="Page not found" text="That address is not part of ClubHub." />,
  },
]);

export default router;
