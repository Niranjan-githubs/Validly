import React, { useState, useEffect, useRef } from 'react';
import { Menu, X, Brain, ChevronRight, ChevronDown, BarChart, Zap, Code, BookOpen, FileText, Users, Settings, LogOut, User, HelpCircle } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { NavLink } from '../../types';
import { signOut } from 'firebase/auth';
import { auth } from '../../firebase';
import { useAuth } from '../../contexts/AuthContext';
import Button from './Button';

interface DropdownItem {
  title: string;
  description: string;
  icon: React.ReactNode;
  href: string;
}

interface NavItem extends NavLink {
  dropdown?: DropdownItem[];
  icon?: React.ReactNode;
}

interface NavbarProps {
  transparent?: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ transparent = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const navLinks: NavItem[] = [
    {
      name: 'Features',
      path: '/#features',
      dropdown: [
        {
          title: 'AI Analysis',
          description: 'Get detailed insights with our AI-powered analysis',
          icon: <BarChart className="w-5 h-5 text-blue-400" />,
          href: '/#ai-analysis',
        },
        {
          title: 'Fast Validation',
          description: 'Quickly validate your startup ideas',
          icon: <Zap className="w-5 h-5 text-yellow-400" />,
          href: '/#validation',
        },
        {
          title: 'API Access',
          description: 'Integrate with our powerful API',
          icon: <Code className="w-5 h-5 text-purple-400" />,
          href: '/#api',
        },
      ],
    },
    { 
      name: 'Resources',
      path: '/resources',
      dropdown: [
        {
          title: 'Documentation',
          description: 'Detailed guides and API references',
          icon: <BookOpen className="w-5 h-5 text-green-400" />,
          href: '/docs',
        },
        {
          title: 'Blog',
          description: 'Latest articles and news',
          icon: <FileText className="w-5 h-5 text-pink-400" />,
          href: '/blog',
        },
        {
          title: 'Community',
          description: 'Join our growing community',
          icon: <Users className="w-5 h-5 text-blue-400" />,
          href: '/community',
        },
      ],
    },
    { name: 'Pricing', path: '/pricing' },
    {
      name: 'Testimonials',
      path: '/#testimonials',
      dropdown: [
        {
          title: '“Validly helped us validate our SaaS idea in days!”',
          description: '— Alex, Startup Founder',
          icon: <span className="text-2xl">🌟</span>,
          href: '/#testimonials',
        },
        {
          title: '“The competitor insights are a game changer.”',
          description: '— Priya, Product Manager',
          icon: <span className="text-2xl">💡</span>,
          href: '/#testimonials',
        },
        {
          title: '“Risk analysis gave us confidence to pitch investors.”',
          description: '— Sam, Co-Founder',
          icon: <span className="text-2xl">🚀</span>,
          href: '/#testimonials',
        },
      ]
    },
  ];

  const userDropdown = [
    {
      title: 'Profile',
      description: 'View and edit your profile',
      icon: <User className="w-5 h-5 text-blue-400" />,
      href: '/profile',
    },
    {
      title: 'Settings',
      description: 'Configure your account settings',
      icon: <Settings className="w-5 h-5 text-purple-400" />,
      href: '/settings',
    },
    {
      title: 'Help & Support',
      description: 'Get help and support',
      icon: <HelpCircle className="w-5 h-5 text-green-400" />,
      href: '/support',
    },
  ];

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setActiveDropdown(null);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const toggleDropdown = (name: string) => {
    setActiveDropdown(activeDropdown === name ? null : name);
  };

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
          <span className="text-white font-bold text-3xl tracking-tight">Validly</span>
        </Link>
      </div>
      {/* Desktop Center: Nav Links and Button */}
      <div className="hidden md:flex flex-1 justify-center items-center gap-x-8">
        {navLinks.map((link) => (
          <div key={link.name} className="relative group" ref={dropdownRef}>
            <button
              onClick={() => link.dropdown && toggleDropdown(link.name)}
              className={`flex items-center text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                activeDropdown === link.name ? 'text-white' : ''
              }`}
            >
              {link.name}
              {link.dropdown && (
                <ChevronDown
                  className={`ml-1 h-4 w-4 transition-transform ${
                    activeDropdown === link.name ? 'transform rotate-180' : ''
                  }`}
                />
              )}
            </button>
            
            {/* Dropdown Menu */}
            {link.dropdown && activeDropdown === link.name && link.name === 'Testimonials' ? (
              <div className="absolute left-1/2 transform -translate-x-1/2 mt-2 w-[600px] rounded-xl bg-black border border-[#222] shadow-xl z-50 overflow-hidden">
                <div className="p-4 flex flex-col gap-4">
                  {link.dropdown.map((item, idx) => (
                    <div key={item.title} className="flex flex-row items-center p-4 rounded-xl bg-black shadow-md min-h-[80px] border border-[#222]">
                      <div className="flex-shrink-0 mr-4 text-3xl">{item.icon}</div>
                      <div className="flex-1">
                        <p className="text-base font-semibold text-white mb-1">{item.title}</p>
                        <p className="text-sm text-purple-300 font-medium mb-1">{item.description}</p>
                        <p className="text-xs text-gray-400">{idx === 0 ? 'We used Validly to validate our SaaS product and received actionable insights that helped us pivot and succeed.' : idx === 1 ? 'The competitor analysis and market trends gave us a clear edge in our product strategy.' : 'Investor risk analysis was spot on and helped us secure funding.'}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : link.dropdown && activeDropdown === link.name ? (
              <div className="absolute left-1/2 transform -translate-x-1/2 mt-2 w-64 rounded-xl bg-[#1a1f2e] border border-[#2d3748] shadow-xl z-50 overflow-hidden">
                <div className="p-2">
                  {link.dropdown.map((item) => (
                    <a
                      key={item.title}
                      href={item.href}
                      className="flex items-start p-3 rounded-lg hover:bg-[#252f3f] transition-colors group/item"
                      onClick={() => setActiveDropdown(null)}
                    >
                      <div className="flex-shrink-0 mt-0.5">
                        {item.icon}
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-white group-hover/item:text-blue-400 transition-colors">
                          {item.title}
                        </p>
                        <p className="text-xs text-gray-400">
                          {item.description}
                        </p>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        ))}

        {!isLoggedIn && !isAuthPage ? (
          <div className="flex items-center gap-4">
            <Link
              to="/login"
              className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Log in
            </Link>
            <Link
            to="/signup"
         className="text-white bg-transparent border border-white/20 px-4 py-2 rounded-full text-sm font-medium transition-all hover:bg-white/10 hover:shadow-lg hover:scale-105 flex items-center"
      >
  Start Validating
  <ChevronRight className="ml-1 h-4 w-4" />
</Link>
          </div>
        ) : (
          <div className="flex items-center gap-4">
            <Link
              to="/chat"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                location.pathname === '/chat' ? 'text-white' : 'text-gray-300 hover:text-white'
              }`}
            >
              Chat
            </Link>
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => toggleDropdown('user')}
                className="flex items-center space-x-2 focus:outline-none"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-medium">
                  {user?.email?.[0]?.toUpperCase() || 'U'}
                </div>
                <ChevronDown
                  className={`h-4 w-4 text-gray-400 transition-transform ${
                    activeDropdown === 'user' ? 'transform rotate-180' : ''
                  }`}
                />
              </button>
              
              {/* User Dropdown */}
              {activeDropdown === 'user' && (
                <div className="absolute right-0 mt-2 w-64 rounded-xl bg-[#1a1f2e] border border-[#2d3748] shadow-xl z-50 overflow-hidden">
                  <div className="p-2">
                    <div className="px-4 py-3 border-b border-[#2d3748] mb-2">
                      <p className="text-sm font-medium text-white">{user?.email || 'User'}</p>
                      <p className="text-xs text-gray-400">Free Plan</p>
                    </div>
                    {userDropdown.map((item) => (
                      <a
                        key={item.title}
                        href={item.href}
                        className="flex items-start p-3 rounded-lg hover:bg-[#252f3f] transition-colors group/item"
                        onClick={() => setActiveDropdown(null)}
                      >
                        <div className="flex-shrink-0 mt-0.5">
                          {item.icon}
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium text-white group-hover/item:text-blue-400 transition-colors">
                            {item.title}
                          </p>
                          <p className="text-xs text-gray-400">
                            {item.description}
                          </p>
                        </div>
                      </a>
                    ))}
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center p-3 rounded-lg hover:bg-red-500/10 text-red-400 hover:text-red-300 transition-colors text-sm font-medium mt-1"
                    >
                      <LogOut className="w-5 h-5 mr-3" />
                      Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
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
          {navLinks.map((link) => (
            <div key={link.name} className="w-full px-4">
              {link.dropdown ? (
                <>
                  <button
                    onClick={() => toggleDropdown(link.name)}
                    className="flex items-center justify-between w-full text-gray-300 hover:text-white px-3 py-2 rounded-md text-base font-medium transition-colors"
                  >
                    <span>{link.name}</span>
                    <ChevronDown
                      className={`h-4 w-4 transition-transform ${
                        activeDropdown === link.name ? 'transform rotate-180' : ''
                      }`}
                    />
                  </button>
                  {activeDropdown === link.name && (
                    <div className="mt-1 ml-4 pl-3 border-l-2 border-gray-700">
                      {link.dropdown.map((item) => (
                        <a
                          key={item.title}
                          href={item.href}
                          className="flex items-start p-2 rounded-lg hover:bg-[#252f3f] transition-colors group/item"
                          onClick={() => {
                            setActiveDropdown(null);
                            setIsOpen(false);
                          }}
                        >
                          <div className="flex-shrink-0 mt-0.5">
                            {item.icon}
                          </div>
                          <div className="ml-3">
                            <p className="text-sm font-medium text-white group-hover/item:text-blue-400 transition-colors">
                              {item.title}
                            </p>
                            <p className="text-xs text-gray-400">
                              {item.description}
                            </p>
                          </div>
                        </a>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <a
                  href={link.path}
                  className="block text-gray-300 hover:text-white px-3 py-2 rounded-md text-base font-medium transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  {link.name}
                </a>
              )}
            </div>
          ))}

          {!isLoggedIn && !isAuthPage ? (
            <div className="w-full px-4 mt-2 space-y-3">
              <Link
                to="/login"
                className="block text-center text-gray-300 hover:text-white px-3 py-2 rounded-md text-base font-medium transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Log in
              </Link>
              <Link
                to="/signup"
                className="block text-center text-white bg-gradient-to-r from-blue-500 to-purple-500 px-4 py-2 rounded-full text-base font-medium transition-all hover:shadow-lg hover:shadow-blue-500/20 hover:scale-105"
                onClick={() => setIsOpen(false)}
              >
                Start Validating
              </Link>
            </div>
          ) : (
            <div className="w-full px-4 mt-2 space-y-3">
              <Link
                to="/chat"
                className={`block text-center px-3 py-2 rounded-md text-base font-medium transition-colors ${
                  location.pathname === '/chat' ? 'text-white' : 'text-gray-300 hover:text-white'
                }`}
                onClick={() => setIsOpen(false)}
              >
                Chat
              </Link>
              <div className="border-t border-gray-800 my-2"></div>
              {userDropdown.map((item) => (
                <a
                  key={item.title}
                  href={item.href}
                  className="flex items-center px-4 py-2 rounded-lg hover:bg-[#252f3f] transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  <div className="flex-shrink-0">
                    {item.icon}
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-white">
                      {item.title}
                    </p>
                    <p className="text-xs text-gray-400">
                      {item.description}
                    </p>
                  </div>
                </a>
              ))}
              <button
                onClick={() => {
                  handleLogout();
                  setIsOpen(false);
                }}
                className="w-full flex items-center justify-center px-4 py-2 rounded-lg hover:bg-red-500/10 text-red-400 hover:text-red-300 transition-colors text-sm font-medium mt-2"
              >
                <LogOut className="w-5 h-5 mr-2" />
                Sign out
              </button>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;