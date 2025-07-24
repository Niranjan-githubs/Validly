import React, { useState, useRef, useEffect } from 'react';
  import { Send, Mic, MicOff } from 'lucide-react';
  import FloatingOrb from '../common/FloatingOrb';
  import Button from '../common/Button';
  import GlassmorphicCard from '../common/GlassmorphicCard';
  import { Message } from '../../types';

  const ChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([
      {
        id: '1',
        content: "Hi there! I'm the Founder Scan AI. Tell me about your startup idea, and I'll help validate it across market trends, competition, and investor potential.",
        sender: 'ai',
        timestamp: new Date(),
      },
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isThinking, setIsThinking] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    
    // Auto-scroll to bottom of messages
    useEffect(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);
    
    useEffect(() => {
      const savedSession = localStorage.getItem('chatSessionId');
      if (savedSession) setSessionId(savedSession);
    }, []);
    
    useEffect(() => {
      if (sessionId) {
        localStorage.setItem('chatSessionId', sessionId);
      }
    }, [sessionId]);
    
    const handleSendMessage = async () => {
      if (!inputValue.trim()) return;
      
      const userMessage: Message = {
        id: Date.now().toString(),
        content: inputValue,
        sender: 'user',
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, userMessage]);
      setInputValue('');
      setIsThinking(true);
      
      try {
        const response = await fetch("http://localhost:8000/api/chat", {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({
            message: inputValue,
            session_id: sessionId,
          }),
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.session_id && !sessionId) {
          setSessionId(data.session_id);
        }
        
        const aiMessage: Message = {
          id: Date.now().toString(),
          content: data.response || "⚠ No response received.",
          sender: 'ai',
          timestamp: new Date(),
        };
        
        setMessages((prev) => [...prev, aiMessage]);
      } catch (error) {
        console.error('API Error:', error);
        const errorMessage: Message = {
          id: Date.now().toString(),
          content: `⚠ API Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
          sender: 'ai',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsThinking(false);
      }
    };
    
    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    };
    
    const toggleRecording = () => {
      setIsRecording(!isRecording);
      
      // Simulate voice recognition
      if (!isRecording) {
        setTimeout(() => {
          setInputValue('I have an idea for a B2B SaaS platform that helps e-commerce companies optimize their shipping logistics.');
          setIsRecording(false);
        }, 3000);
      }
    };

    return (
      <div className="flex flex-col h-screen bg-black pt-16">
        {/* Background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-0 right-0 h-64 bg-black"></div>
          <div className="absolute inset-0 bg-black opacity-100"></div>
        </div>
        
        <div className="flex-1 overflow-hidden flex flex-col relative">
          <div className="px-4 py-3 border-b border-gray-800 bg-black backdrop-blur-md flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 z-50 relative">
            <div className="flex items-center">
              <FloatingOrb size="sm" />
              <h1 className="text-xl font-semibold text-white ml-2">🧠 Idea Agent – Let's Understand Your Startup</h1>
            </div>
            <button
              className="bg-transparent text-white font-semibold px-4 py-2 rounded shadow transition-colors border border-white hover:bg-white/10"
              onClick={() => {
                setSessionId(null);
                setMessages([
                  {
                    id: '1',
                    content: "Hi there! I'm the Founder Scan AI. Tell me about your startup idea, and I'll help validate it across market trends, competition, and investor potential.",
                    sender: 'ai',
                    timestamp: new Date(),
                  },
                ]);
                localStorage.removeItem('chatSessionId');
              }}
              title="Start a new chat session"
            >
              New Chat
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-black">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.sender === 'ai' && (
                  <div className="mr-3 flex items-end">
                    <FloatingOrb size="sm" isThinking={isThinking && messages[messages.length - 1].id === message.id} />
                  </div>
                )}
                <GlassmorphicCard 
                  className={`max-w-[75%] p-4 rounded-xl border-2 shadow-lg bg-black border-gray-800`}
                >
                  <p className="text-gray-200 text-base leading-relaxed">{message.content}</p>
                </GlassmorphicCard>
                {message.sender === 'user' && (
                  <div className="ml-3 flex items-end">
                    <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          
          <div className="p-4">
            <GlassmorphicCard className="flex items-center p-2 bg-black border-2 border-gray-800 rounded-xl shadow-lg">
              <button 
                className={`p-2 rounded-full mr-2 transition-colors ${
                  isRecording 
                    ? 'bg-red-500 text-white animate-pulse' 
                    : 'bg-black text-gray-400 hover:text-white hover:bg-gray-700 border border-gray-800'
                }`}
                onClick={toggleRecording}
              >
                {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </button>
              <textarea
                className="flex-1 bg-transparent border-none text-white placeholder-gray-500 resize-none max-h-32 focus:outline-none text-base"
                placeholder={isRecording ? "Listening..." : "Type your message..."}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                disabled={isRecording}
              />
              <Button 
                variant="primary" 
                size="sm" 
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isThinking}
                className="ml-2 bg-black border border-gray-800 text-white shadow-lg hover:bg-gray-800"
              >
                <Send className="h-4 w-4" />
              </Button>
            </GlassmorphicCard>
            
            {isRecording && (
              <div className="mt-4 flex justify-center">
                <div className="relative">
                  <div className="absolute inset-0 bg-red-500 rounded-full animate-ping opacity-25"></div>
                  <div className="relative flex items-center justify-center rounded-full h-16 w-16 bg-gradient-to-r from-red-500 to-purple-500">
                    <div className="wave-container">
                      {[...Array(5)].map((_, i) => (
                        <div key={i} className={`wave wave-${i + 1}`}></div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
        
        <style>{`
          .bg-grid-pattern {
            background-image: 
              linear-gradient(rgba(30, 41, 59, 0.3) 1px, transparent 1px),
              linear-gradient(90deg, rgba(30, 41, 59, 0.3) 1px, transparent 1px);
            background-size: 40px 40px;
          }
          
          .wave-container {
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          
          .wave {
            position: absolute;
            width: 100%;
            height: 100%;
            border: 2px solid white;
            border-radius: 50%;
            opacity: 0;
            animation: wave 2s infinite;
          }
          
          .wave-1 { animation-delay: 0.2s; }
          .wave-2 { animation-delay: 0.4s; }
          .wave-3 { animation-delay: 0.6s; }
          .wave-4 { animation-delay: 0.8s; }
          
          @keyframes wave {
            0% {
              transform: scale(0.5);
              opacity: 0.8;
            }
            100% {
              transform: scale(1.5);
              opacity: 0;
            }
          }
        `}</style>
      </div>
    );
  };

  // User Avatar Component
  const User: React.FC<{ className?: string }> = ({ className = '' }) => {
    return (
      <svg
        className={className}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 12C14.2091 12 16 10.2091 16 8C16 5.79086 14.2091 4 12 4C9.79086 4 8 5.79086 8 8C8 10.2091 9.79086 12 12 12Z"
          fill="currentColor"
        />
        <path
          d="M12 14C8.13401 14 5 17.134 5 21H19C19 17.134 15.866 14 12 14Z"
          fill="currentColor"
        />
      </svg>
    );
  };

  export default ChatInterface;