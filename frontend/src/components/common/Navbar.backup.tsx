import React, { useState, useEffect } from 'react';
import { Menu, X, Brain, ChevronRight } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { NavLink } from '../../types';
import { signOut } from 'firebase/auth';
import { auth } from '../../firebase';
import { useAuth } from '../../contexts/AuthContext';
import Button from './Button';

interface NavbarProps {
  transparent?: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ transparent = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  const navLinks: NavLink[] = [
    { name: 'Features', path: '/#features' },
    { name: 'Testimonials', path: '/#testimonials' },
    { name: 'Pricing', path: '/#pricing' },
    { name: 'Community', path: '/#community' },
  ];

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isAuthPage = location.pathname === '/login' || location.pathname === '/signup';
  const isLoggedIn = location.pathname === '/chat' || location.pathname === '/dashboard';

  const handleLogout = async () => {
    try {
      await signOut(auth);
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <nav className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[90vw] max-w-5xl bg-[#10131a] bg-opacity-90 rounded-full shadow-lg border border-[#23263a] flex items-center px-4 py-2 backdrop-blur-md`}>
      {/* Left: Logo and Brand */}
      <div className="flex items-center min-w-[150px]">
        <Link to="/" className="flex items-center space-x-2">
          <span className="text-white font-bold text-xl tracking-tight">FounderScan</span>
        </Link>
      </div>
      {/* Desktop Center: Nav Links and Button */}
      <div className="hidden md:flex flex-1 justify-center items-center gap-x-8">
        {!isLoggedIn && navLinks.map((link) => (
          <a
            key={link.name}
            href={link.path}
            className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
          >
            {link.name}
          </a>
        ))}
        {!isLoggedIn && !isAuthPage && (
          <>
            <Link
              to="/login"
              className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Log in
            </Link>
            <Link
              to="/signup"
              className="text-white px-4 py-2 rounded-full text-sm font-medium transition-transform hover:scale-105 flex items-center ml-4"
            >
              Start Validating
              <ChevronRight className="ml-1 h-4 w-4" />
            </Link>
          </>
        )}
        {isLoggedIn && (
          <>
            <Link
              to="/chat"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                location.pathname === '/chat' ? 'text-white' : 'text-gray-300 hover:text-white'
              }`}
            >
              Chat
            </Link>
            <Link
              to="/dashboard"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                location.pathname === '/dashboard' ? 'text-white' : 'text-gray-300 hover:text-white'
              }`}
            >
              Dashboard
            </Link>
            <Button
              variant="outline"
              onClick={handleLogout}
              className="text-sm"
            >
              Logout
            </Button>
          </>
        )}
      </div>
      {/* Hamburger for mobile */}
      <div className="flex md:hidden flex-1 justify-end">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white focus:outline-none"
        >
          {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>
      {/* Mobile menu */}
      {isOpen && (
        <div className="absolute top-full left-0 w-full bg-[#10131a] rounded-b-2xl shadow-lg border-t border-[#23263a] flex flex-col items-center py-4 md:hidden z-50">
          {!isLoggedIn && navLinks.map((link) => (
            <a
              key={link.name}
              href={link.path}
              className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-base font-medium transition-colors w-full text-center"
              onClick={() => setIsOpen(false)}
            >
              {link.name}
            </a>
          ))}
          {!isLoggedIn && !isAuthPage && (
            <>
              <Link
                to="/login"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-base font-medium transition-colors w-full text-center"
                onClick={() => setIsOpen(false)}
              >
                Log in
              </Link>
              <Link
                to="/signup"
                className="text-white px-4 py-2 rounded-full text-base font-medium transition-transform hover:scale-105 flex items-center justify-center mt-2"
                onClick={() => setIsOpen(false)}
              >
                Start Validating
                <ChevronRight className="ml-1 h-4 w-4" />
              </Link>
            </>
          )}
          {isLoggedIn && (
            <>
              <Link
                to="/chat"
                className={`px-3 py-2 rounded-md text-base font-medium transition-colors w-full text-center ${
                  location.pathname === '/chat' ? 'text-white' : 'text-gray-300 hover:text-white'
                }`}
                onClick={() => setIsOpen(false)}
              >
                Chat
              </Link>
              <Link
                to="/dashboard"
                className={`px-3 py-2 rounded-md text-base font-medium transition-colors w-full text-center ${
                  location.pathname === '/dashboard' ? 'text-white' : 'text-gray-300 hover:text-white'
                }`}
                onClick={() => setIsOpen(false)}
              >
                Dashboard
              </Link>
              <Button
                variant="outline"
                onClick={handleLogout}
                className="text-base w-full mt-2"
              >
                Logout
              </Button>
            </>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;