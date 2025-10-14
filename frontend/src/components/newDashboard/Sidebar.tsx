import React from 'react';
import { ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';

interface Session {
  session_id: string;
  initial_idea: string;
  analysis_status?: string;
  created_at?: string;
}

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  onSessionSelect?: (sessionId: string) => void;
}


// Sign out button component
function SidebarSignOut() {
  const [loading, setLoading] = React.useState(false);
  const handleSignOut = async () => {
    setLoading(true);
    try {
      const { auth } = await import('../../firebase');
      await auth.signOut();
      window.location.href = '/login';
    } catch (err) {
      // Optionally show error
    } finally {
      setLoading(false);
    }
  };
  return (
    <div
      className="w-full flex justify-center items-end fixed left-0 z-30"
      style={{
        bottom: 0,
        // Responsive width for open/closed sidebar
        width: 'inherit',
        minWidth: 0,
        maxWidth: '100vw',
        background: 'transparent',
        pointerEvents: 'auto',
      }}
    >
      <button
        onClick={handleSignOut}
        disabled={loading}
        className="w-full flex items-center gap-2 px-4 py-3 rounded-none bg-black text-white font-semibold shadow-lg hover:bg-neutral-900 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed border-t border-blue-500/10"
        style={{ minWidth: 120, borderRadius: 0, borderBottomLeftRadius: 0, borderBottomRightRadius: 0 }}
      >
        {loading ? (
          <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="4" strokeLinecap="round" /></svg>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h4a2 2 0 012 2v1" /></svg>
        )}
        <span>Sign Out</span>
      </button>
    </div>
  );
}

const Sidebar = ({ collapsed, onToggle, onSessionSelect }: SidebarProps): JSX.Element => {
  const [sessions, setSessions] = React.useState<Session[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [selectedSessionId, setSelectedSessionId] = React.useState<string | null>(() => {
    // Try to restore from localStorage
    return localStorage.getItem('sidebar_selectedSessionId') || null;
  });

  // On mount, if a session is already selected, notify parent
  React.useEffect(() => {
    if (selectedSessionId && onSessionSelect) {
      onSessionSelect(selectedSessionId);
    }
    // eslint-disable-next-line
  }, [selectedSessionId]);

  const fetchSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get the current Firebase user and fetch a fresh ID token
      const { auth } = await import('../../firebase');
      const user = auth.currentUser;
      if (!user) throw new Error('Authentication required. Please log in again.');
      const token = await user.getIdToken();
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/api/chat/sessions`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      let data = null;
      try {
        data = await response.json();
      } catch (jsonErr) {
        // Optionally handle JSON parse error
      }
      if (!response.ok) throw new Error('Failed to fetch sessions');
      // If the response is an array, set it directly; if it's an object with sessions, use that
      let sessionsArr = [];
      if (Array.isArray(data)) {
        sessionsArr = data;
      } else if (data && Array.isArray(data.sessions)) {
        sessionsArr = data.sessions;
      }
      // Sort descending by created_at (or fallback to session_id)
      sessionsArr.sort((a: Session, b: Session) => {
        if (a.created_at && b.created_at) {
          return (b.created_at || '').localeCompare(a.created_at || '');
        }
        // fallback: sort by session_id (descending)
        return (b.session_id || '').localeCompare(a.session_id || '');
      });
      setSessions(sessionsArr);
      // Only auto-select if nothing is selected and no sessionId in localStorage
      if (sessionsArr.length > 0 && !selectedSessionId) {
        const storedId = localStorage.getItem('sidebar_selectedSessionId');
        if (storedId && sessionsArr.some((s: Session) => s.session_id === storedId)) {
          setSelectedSessionId(storedId);
          if (onSessionSelect) onSessionSelect(storedId);
        } else {
          setSelectedSessionId(sessionsArr[0].session_id);
          if (onSessionSelect) onSessionSelect(sessionsArr[0].session_id);
        }
      }
    } catch (err) {
      console.error('[Sidebar] Fetch sessions error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchSessions();
    // eslint-disable-next-line
  }, []);

  return (
    <>
      {/* Mobile floating access button */}
      <button
        className={`fixed left-4 bottom-6 z-[60] p-2 sm:p-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg text-white transition-all duration-300 lg:hidden ${!collapsed ? 'hidden' : ''}`}
        style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
        onClick={onToggle}
        aria-label="Open sidebar"
      >
        <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
      </button>
      {/* Sidebar overlay for mobile when open */}
      <div
        className={`fixed inset-0 bg-black/40 z-40 transition-opacity duration-300 lg:hidden ${collapsed ? 'pointer-events-none opacity-0' : 'pointer-events-auto opacity-100'}`}
        onClick={onToggle}
        aria-hidden="true"
      />
      <div
        className={`fixed left-0 top-0 h-full bg-black backdrop-blur-xl border-r border-[#333333] hover:border-blue-400/30 transition-all duration-500 z-50 flex flex-col
        ${collapsed ? 'w-0 sm:w-16 -translate-x-full lg:w-16 lg:translate-x-0' : 'w-64 translate-x-0'}
        shadow-2xl shadow-black/50
        ${collapsed ? 'lg:w-16' : 'lg:w-64'}
        ${collapsed ? 'lg:translate-x-0' : ''}
        `}
        style={{ maxWidth: '90vw', minWidth: collapsed ? 0 : undefined, overflow: 'hidden' }}
        aria-label="Sidebar navigation"
      >
        {/* Header always at the top */}
        <div className="relative z-20 flex items-center justify-between p-4 sm:p-6 border-b border-[#333333] hover:border-blue-400/30 transition-colors duration-500 bg-black/80 sticky top-0">
          {!collapsed && (
            <div className="flex items-center gap-4 animate-fade-in">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl blur-lg opacity-30 animate-pulse"></div>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent">Validly</span>
            </div>
          )}
          <button
            onClick={onToggle}
            className={`p-2 sm:p-3 rounded-xl hover:bg-gradient-to-r hover:from-[#333333] hover:to-[#444444] transition-all duration-300 text-[#CCCCCC] hover:text-white border border-transparent hover:border-blue-400/30 hover:shadow-lg hover:shadow-blue-500/25 ${collapsed ? 'mx-auto' : ''} ${collapsed ? 'hidden lg:block' : ''}`}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5" /> : <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5" />}
          </button>
        </div>

        {/* Session List */}
        <nav
          className={`relative z-10 flex-1 overflow-y-auto ${collapsed ? 'flex flex-col items-center justify-center py-8 gap-6' : 'p-2 sm:p-6'}`}
          style={{ scrollbarColor: '#222 #000', scrollbarWidth: 'thin' }}
        >
          {!collapsed && (
            <div className="mt-6">
              <h3 className="text-1xl font-extrabold text-white mb-4 px-2 tracking-wide">Your Sessions</h3>
              {loading && <div className="text-blue-400 px-2">Loading sessions...</div>}
              {error && <div className="text-red-400 px-2">{error}</div>}
              <div className="flex flex-col gap-3">
                {sessions.map((session) => (
                  <button
                    key={session.session_id}
                    onClick={() => {
                      setSelectedSessionId(session.session_id);
                      localStorage.setItem('sidebar_selectedSessionId', session.session_id);
                      // onSessionSelect will be called by useEffect
                      // Always close sidebar on session select
                      onToggle();
                    }}
                    className={`w-full flex items-center justify-between px-6 py-4 rounded-2xl bg-black border ${selectedSessionId === session.session_id ? 'border-blue-400/60 bg-blue-500/10 shadow-blue-500/30' : 'border-[#23263a]'} shadow-lg hover:shadow-blue-500/20 transition-all duration-300 text-base text-white font-semibold hover:bg-blue-500/10 hover:border-blue-400/30 cursor-pointer backdrop-blur-md`}
                    style={{ minHeight: 56, fontSize: '1rem', letterSpacing: '0.02em' }}
                  >
                    <span className="truncate text-lg font-medium">{session.initial_idea || 'Untitled Session'}</span>
                    <span className="ml-2 text-xs text-blue-400">{session.session_id.slice(-6)}</span>
                  </button>
                ))}
              </div>
              <button
                onClick={fetchSessions}
                className="mt-4 flex items-center gap-2 text-blue-400 hover:text-blue-200 text-sm px-2 py-1 rounded-lg border border-blue-400/20 hover:border-blue-400/40 bg-blue-500/5 hover:bg-blue-500/10 transition-all duration-300"
              >
                <RefreshCw className="w-4 h-4" /> Refresh
              </button>
            </div>
          )}
        </nav>
        {/* Removed sidebar background gradient for cleaner look */}
        <style>{`
          nav::-webkit-scrollbar {
            width: 8px;
            background: #000;
          }
          nav::-webkit-scrollbar-thumb {
            background: #222;
            border-radius: 8px;
          }
        `}</style>
        {/* Sign Out Button at the bottom */}
        <SidebarSignOut />
      </div>
    </>
  );
};

export default Sidebar; 