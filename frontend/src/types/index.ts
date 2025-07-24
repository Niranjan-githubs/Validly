export interface NavLink {
  name: string;
  path: string;
}

export interface Feature {
  icon: string;
  title: string;
  description: string;
  color: string;
}

export interface Testimonial {
  id: number;
  name: string;
  role: string;
  company: string;
  avatar: string;
  content: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
}

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isTyping?: boolean;
}

export interface AgentCard {
  id: string;
  title: string;
  icon: string;
  description: string;
  status: 'active' | 'idle' | 'processing';
  color: string;
  progress: number;
  insights?: string[];
}