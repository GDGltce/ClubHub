import { useState } from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

export default function AppLayout({ children, hideSidebar = false }) {
  const [open, setOpen] = useState(false);

  return (
    <div className={`app-layout${hideSidebar ? ' app-layout--no-sidebar' : ''}`}>
      <Navbar onMenu={() => setOpen(true)} />
      {!hideSidebar && (
        <>
          {open && <button className="sidebar-backdrop" aria-label="Close menu" onClick={() => setOpen(false)} />}
          <Sidebar open={open} onNavigate={() => setOpen(false)} />
        </>
      )}
      <main className="main-content">{children}</main>
    </div>
  );
}
