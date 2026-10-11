import { useState } from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

export default function AppLayout({ children, hideSidebar = false }) {
  const [open, setOpen] = useState(false);

  const closeMenu = () => setOpen(false);

  return (
    <div className={`app-layout${hideSidebar ? ' app-layout--no-sidebar' : ''}`}>
      <Navbar
        menuOpen={open}
        onMenu={() => setOpen((current) => !current)}
      />

      {!hideSidebar && (
        <>
          {open && (
            <button
              className="sidebar-backdrop"
              type="button"
              aria-label="Close navigation menu"
              onClick={closeMenu}
            />
          )}

          <Sidebar
            open={open}
            onNavigate={closeMenu}
          />
        </>
      )}

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}