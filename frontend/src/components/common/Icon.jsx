const PATHS = {
  home: (
    <>
      <path d="M4 10.5 12 4l8 6.5" />
      <path d="M6 9.5V20h12V9.5" />
      <path d="M10 20v-6h4v6" />
    </>
  ),
  clubs: (
    <>
      <circle cx="12" cy="12" r="8" />
      <circle cx="12" cy="12" r="3" />
      <path d="M12 4v2M12 18v2M4 12h2M18 12h2" />
    </>
  ),
  calendar: (
    <>
      <rect x="4" y="5" width="16" height="15" rx="1" />
      <path d="M8 3.5V7M16 3.5V7M4 10h16" />
    </>
  ),
  chat: (
    <>
      <path d="M5 6h14v9H8l-3 3V6z" />
    </>
  ),
  file: (
    <>
      <path d="M7 3.5h7l4 4V20.5H7z" />
      <path d="M14 3.5V8h4" />
      <path d="M9.5 13h5M9.5 16h5" />
    </>
  ),
  building: (
    <>
      <path d="M4 20.5h16" />
      <path d="M6 20.5V6.5h8v14" />
      <path d="M14 10.5h4v10" />
      <path d="M8.5 9.5h3M8.5 13h3M8.5 16.5h3" />
    </>
  ),
  users: (
    <>
      <circle cx="9" cy="9" r="2.5" />
      <circle cx="16" cy="10" r="2" />
      <path d="M4.5 18.5c.6-2.4 2.4-3.5 4.5-3.5s3.9 1.1 4.5 3.5" />
      <path d="M14 15.2c1.3-.3 2.6.1 3.5 1.1.7.8 1 1.6 1.2 2.2" />
    </>
  ),
  bell: (
    <>
      <path d="M6 16.5h12l-1.2-2V11a4.8 4.8 0 0 0-9.6 0v3.5z" />
      <path d="M10 16.5a2 2 0 0 0 4 0" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="5.5" />
      <path d="M15.5 15.5 20 20" />
    </>
  ),
  plus: <path d="M12 6v12M6 12h12" />,
  logout: (
    <>
      <path d="M10 7V5.5h9V18.5h-9V17" />
      <path d="M4 12h9" />
      <path d="M10 9l3 3-3 3" />
    </>
  ),
  arrow: <path d="M5 12h14M13 6l6 6-6 6" />,
  check: <path d="M5 12.5 9.5 17 19 7" />,
  instagram: (
    <>
      <rect x="4.5" y="4.5" width="15" height="15" rx="3" />
      <circle cx="12" cy="12" r="3.2" />
      <circle cx="16.6" cy="7.4" r="0.7" fill="currentColor" stroke="none" />
    </>
  ),
  menu: <path d="M4 7h16M4 12h16M4 17h16" />,
  close: <path d="M6 6l12 12M18 6 6 18" />,
};

export default function Icon({ name, size = 18 }) {
  return (
    <svg
      className="icon"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {PATHS[name]}
    </svg>
  );
}

export function Mark({ size = 28 }) {
  return (
    <svg className="mark" width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <rect x="1" y="1" width="30" height="30" rx="2" fill="none" stroke="currentColor" strokeWidth="1.5" />
      <path d="M10 22V10h6.2a4.2 4.2 0 0 1 0 8.4H10" fill="none" stroke="currentColor" strokeWidth="1.7" />
      <path d="M16.2 18.4 22 22" fill="none" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}
