import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { storeUserOutput, getUserOutput } from '../utils/firestore';
import Navbar from '../components/common/Navbar';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import styles from './ChatPage.module.css';

interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const welcomeMessage: ChatMessage = {
  id: '1',
  content: "Tell me about your startup idea , we'll discuss it together and build it together and let the founderscan plays the validation.",
  sender: 'ai',
  timestamp: new Date(),
};

const ChatPage: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load previous chat history when component mounts
  useEffect(() => {
    const loadChatHistory = async () => {
      if (user) {
        console.log('Loading chat history for user:', user.uid);
        try {
          const data = await getUserOutput(user);
          console.log('Loaded chat history:', data);
          if (data?.output?.messages) {
            setMessages(data.output.messages as ChatMessage[]);
          }
        } catch (error) {
          console.error('Error loading chat history:', error);
        }
      }
    };

    loadChatHistory();
  }, [user]);

  // Handle video loop with slower playback
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.playbackRate = 0.75; // Slower playback speed
      videoRef.current.play().catch(error => {
        console.error('Error playing video:', error);
      });
    }
  }, []);

  // Handle text-to-speech
  const speakResponse = async (text: string) => {
    try {
      setIsSpeaking(true);
      const response = await fetch('http://localhost:8000/api/chat/audio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) throw new Error('Failed to get audio');
      
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        await audioRef.current.play();
      }
    } catch (error) {
      console.error('Error playing audio:', error);
    } finally {
      setIsSpeaking(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !user) return;

    setLoading(true);
    try {
      // Add user message
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        content: input,
        sender: 'user',
        timestamp: new Date(),
      };
      const newMessages = [...messages, userMessage];
      setMessages(newMessages);
      setInput('');

      // Call the API
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          session_id: sessionId,
        }),
      });

      if (!res.ok) {
        throw new Error(`API Error: ${res.status}`);
      }

      const data = await res.json();
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: data.response || '⚠️ No response received from API.',
        sender: 'ai',
        timestamp: new Date(),
      };
      const updatedMessages = [...newMessages, aiMessage];
      setMessages(updatedMessages);
      
      // Speak the AI response
      await speakResponse(data.response);

      await storeUserOutput(user, {
        messages: updatedMessages,
        lastUpdated: new Date()
      });
      if (data.done) {
        try {
          const summaryRes = await fetch('http://localhost:8000/api/chat/summary', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
            body: JSON.stringify({ session_id: data.session_id }),
          });
  
          if (!summaryRes.ok) {
            throw new Error(`Summary API Error: ${summaryRes.status}`);
          }
  
          const summaryData = await summaryRes.json();
          const summaryMessage: ChatMessage = {
            id: (Date.now() + 2).toString(),
            content: `📝 Summary:\n${JSON.stringify(summaryData.summary, null, 2)}`,
            sender: 'ai',
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, summaryMessage]);
        } catch (error) {
          console.error('Error fetching summary:', error);
          const errorMessage: ChatMessage = {
            id: (Date.now() + 3).toString(),
            content: `⚠️ Error fetching summary: ${error instanceof Error ? error.message : 'Unknown error'}`,
            sender: 'ai',
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errorMessage]);
        }
      }




    } catch (error) {
      console.error('Error in chat:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 2).toString(),
        content: `⚠️ API Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-transparent relative overflow-hidden">

      <Navbar />
      <audio ref={audioRef} className="hidden" />
      
      <div className="max-w-7xl mx-auto pt-20 px-4 relative">
        <div className="flex gap-6">
          {/* Video Avatar Section */}
          <div className="hidden lg:block w-72 flex-shrink-0">
            <div className="sticky top-24 bg-gray-800/30 backdrop-blur-xl rounded-xl shadow-2xl overflow-hidden border border-purple-500/20 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-purple-500/20">
              <div className="relative aspect-[9/16] w-full">
                <video
                  ref={videoRef}
                  className="w-full h-full object-cover"
                  loop
                  muted
                  playsInline
                  src="/video avatar.mp4"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900/90 via-gray-900/50 to-transparent" />
                {isSpeaking && (
                  <div className="absolute bottom-3 left-1/2 transform -translate-x-1/2 flex space-x-1">
                    {[...Array(3)].map((_, i) => (
                      <div
                        key={i}
                        className={`w-1.5 h-4 bg-purple-500 rounded-full animate-sound-wave`}
                        style={{
                          animationDelay: `${i * 0.1}s`,
                          animationDuration: '0.5s'
                        }}
                      />
                    ))}
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-gray-900/80" />
              </div>
              <div className="p-4 text-center relative">
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900/80 to-transparent" />
                <div className="relative">
                  <h3 className="text-lg font-medium text-white mb-1 bg-clip-text text-transparent bg-gradient-to-r from-purple-300 to-pink-300">AI Assistant</h3>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Section */}
          <div className="flex-1">
            <div className="bg-gray-800/40 backdrop-blur-xl rounded-xl shadow-2xl p-4 mb-4 border border-purple-500/20 transform transition-all duration-300">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-purple-800 flex items-center justify-center shadow-lg shadow-purple-500/20 transform transition-transform hover:scale-105">
                    <span className="text-lg">🤖</span>
                  </div>
                  <div>
                    <div className="text-lg font-medium bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-400">Validator</div>
                    <div className="text-xs text-gray-400">Let's discuss your idea</div>
                  </div>
                </div>
                <button
                  className="bg-gradient-to-r from-purple-600 to-purple-800 hover:from-purple-700 hover:to-purple-900 text-white font-medium px-4 py-2 rounded-lg shadow-lg shadow-purple-500/20 transition-all duration-300 hover:shadow-purple-500/40 hover:scale-105 border border-purple-500/30 text-sm"
                  onClick={() => {
                    setMessages([welcomeMessage]);
                    setSessionId(null);
                    localStorage.removeItem('chatSessionId');
                  }}
                  title="Start a new chat session"
                >
                  New Chat
                </button>
              </div>

              {/* Messages Container */}
              <div className={`space-y-3 h-[60vh] overflow-y-auto mb-4 ${styles.customScrollbar} pr-2`}>
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${
                      message.sender === 'user' ? 'justify-end' : 'justify-start'
                    } ${styles.animateFadeIn}`}
                  >
                    {message.sender === 'ai' && (
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-purple-800 flex items-center justify-center mr-2 flex-shrink-0 shadow-lg shadow-purple-500/20">
                        <span className="text-sm">🤖</span>
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-xl p-3 text-sm ${
                        message.sender === 'user'
                          ? 'bg-gradient-to-r from-purple-600 to-purple-800 text-white shadow-lg shadow-purple-500/20'
                          : 'bg-gray-700/80 text-gray-200 shadow-lg shadow-gray-900/20 backdrop-blur-sm'
                      } transform transition-all duration-300 hover:scale-[1.02]`}
                    >
                      {message.content}
                    </div>
                    {message.sender === 'user' && (
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center ml-2 flex-shrink-0 shadow-lg shadow-purple-500/20">
                        <span className="text-sm">👤</span>
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Form */}
              <form onSubmit={handleSubmit} className="flex gap-2">
                <Input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 bg-gray-700/50 border-purple-500/20 focus:border-purple-500/40 text-white placeholder-gray-400 rounded-lg px-3 py-2 text-sm shadow-lg shadow-purple-500/10 transition-all duration-300 focus:shadow-purple-500/20"
                />
                <Button
                  type="submit"
                  variant="primary"
                  disabled={loading || !input.trim()}
                  className="bg-gradient-to-r from-purple-600 to-purple-800 hover:from-purple-700 hover:to-purple-900 text-white px-4 py-2 rounded-lg shadow-lg shadow-purple-500/20 transition-all duration-300 hover:shadow-purple-500/40 hover:scale-105 disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-none text-sm"
                >
                  {loading ? (
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                      <span>Sending...</span>
                    </div>
                  ) : (
                    'Send'
                  )}
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;