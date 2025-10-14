import React, { useState, useEffect, useRef } from 'react';
import Spline from '@splinetool/react-spline';
import { useAuth } from '../contexts/AuthContext';
import { storeUserOutput, getUserOutput } from '../utils/firestore';
import Navbar from '../components/common/Navbar';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import styles from './ChatPage.module.css';
import { auth } from '../firebase';

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
   const [analysisStarted, setAnalysisStarted] = useState(false);
   const videoRef = useRef<HTMLVideoElement>(null);
   const messagesEndRef = useRef<HTMLDivElement>(null);
   const audioRef = useRef<HTMLAudioElement>(null);
   // Removed animation loading state
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
         try {
           const data = await getUserOutput(user);
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
 
   // Manual analysis trigger
   const handleRunAnalysis = async () => {
     if (!sessionId || !user) return;
     setLoading(true);
     try {
       const currentUser = auth.currentUser;
       if (!currentUser) throw new Error('Not authenticated');
       const token = await currentUser.getIdToken();
       await fetch('http://localhost:8000/api/analysis/start', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
           'Accept': 'application/json',
           'Authorization': `Bearer ${token}`,
         },
         body: JSON.stringify({
           startup_data: {
             session_id: sessionId,
           }
         }),
       });
       setAnalysisStarted(true);
     } catch (error) {
       // Optionally show error
     } finally {
       setLoading(false);
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
       // Add a temporary 'thinking...' AI message
       const thinkingMessage: ChatMessage = {
         id: (Date.now() + 0.5).toString(),
         content: 'Thinking... ',
         sender: 'ai',
         timestamp: new Date(),
       };
       const newMessages = [...messages, userMessage, thinkingMessage];
       setMessages(newMessages);
       setInput('');

       // Get Firebase ID token
       const currentUser = auth.currentUser;
       if (!currentUser) throw new Error('Not authenticated');
       const token = await currentUser.getIdToken();

       // Call the API
       const res = await fetch('http://localhost:8000/api/chat', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
           'Accept': 'application/json',
           'Authorization': `Bearer ${token}`,
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

       // Replace the 'thinking...' message with the real response
       const aiMessage: ChatMessage = {
         id: (Date.now() + 1).toString(),
         content: data.response || '⚠️ No response received from API.',
         sender: 'ai',
         timestamp: new Date(),
       };
       setMessages((prev) => {
         // Remove the last message if it's the thinking message
         const prevWithoutThinking = prev.slice(0, -1);
         return [...prevWithoutThinking, aiMessage];
       });
       
       // Speak the AI response
       await speakResponse(data.response);

       await storeUserOutput(user, {
         messages: [...newMessages.slice(0, -1), aiMessage],
         lastUpdated: new Date()
       });
       // Remove auto-trigger; user must click the button

     } catch (error) {
       console.error('Error in chat:', error);
       // Remove the thinking message if present, then add error
       setMessages((prev) => {
         const prevWithoutThinking = prev[prev.length - 1]?.content === 'Thinking... 🤔' ? prev.slice(0, -1) : prev;
         const errorMessage: ChatMessage = {
           id: (Date.now() + 2).toString(),
           content: `⚠️ API Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
           sender: 'ai',
           timestamp: new Date(),
         };
         return [...prevWithoutThinking, errorMessage];
       });
     } finally {
       setLoading(false);
     }
   };
 
   return (
    <div className="min-h-screen relative overflow-hidden bg-black">
      {/* Spline Animation Background */}
      <div className="absolute inset-0 w-full h-full z-0" style={{ transform: 'translateX(-86px)' }}>
        <Spline scene="https://prod.spline.design/uvpIzpyAVFuW7VLx/scene.splinecode" />
      </div>
 
       <Navbar />
       <audio ref={audioRef} className="hidden" />
       
       <div className="max-w-7xl mx-auto pt-20 px-4 relative">
        <div className="flex gap-6">
          {/* Chat Section Only */}
          <div className="flex-1 flex flex-col items-end justify-end relative z-10" style={{ pointerEvents: 'none' }}>
            <div
              className="w-full max-w-[170vh] h-[86vh] mb-2 bg-black backdrop-blur-xl rounded-2xl shadow-2xl flex flex-col border border-gray-700/40 p-4 fixed right-[18px] bottom-[9px] z-20 pointer-events-none"
              style={{ pointerEvents: 'none' }}
            >
               <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4" style={{ pointerEvents: 'none' }}>
                 <div className="flex items-center gap-3">
                   <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-black to-gray-800 flex items-center justify-center shadow-lg shadow-black/20 transform transition-transform hover:scale-105">
                      <span className="text-lg">🤖</span>
                    </div>
                   <div>
                     <div className="text-lg font-medium text-white">Validator</div>
                    <div className="text-xs text-white">Let's discuss your idea</div>
                   </div>
                 </div>
                <button
                  className="bg-transparent text-white font-medium px-4 py-2 rounded-lg shadow-lg transition-all duration-300 border border-gray-700/40 text-sm hover:scale-105 hover:shadow-gray-500/40"
                  onClick={() => {
                    setMessages([welcomeMessage]);
                    setSessionId(null);
                    localStorage.removeItem('chatSessionId');
                  }}
                  title="Start a new chat session"
                  style={{ pointerEvents: 'auto' }}
                >
                  New Chat
                </button>
               </div>

               {/* Messages Container */}
               <div className={`space-y-3 h-[60vh] overflow-y-auto mb-4 ${styles.customScrollbar} pr-2 bg-black rounded-xl p-2`} style={{ pointerEvents: 'none' }}>
                 {messages.map((message, index) => (
                   <div
                     key={index}
                     className={`flex ${
                       message.sender === 'user' ? 'justify-end' : 'justify-start'
                     } ${styles.animateFadeIn}`}
                   >
                     {message.sender === 'ai' && (
                       <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gray-900 to-gray-700 flex items-center justify-center mr-2 flex-shrink-0 shadow-lg shadow-gray-900/20">
                         <span className="text-sm">🤖</span>
                       </div>
                     )}
                     <div
                     className={`max-w-[80%] rounded-xl p-3 text-sm ${
                       message.sender === 'user'
                         ? 'bg-black text-white shadow-lg shadow-gray-900/20'
                         : 'bg-gray-800 text-gray-200 shadow-lg shadow-gray-900/20 backdrop-blur-sm'
                     } transform transition-all duration-300 hover:scale-[1.02]`}
                     style={{ pointerEvents: 'none' }}
                     >
                       {message.content}
                     </div>
                     {message.sender === 'user' && (
                       <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gray-900 to-gray-700 flex items-center justify-center ml-2 flex-shrink-0 shadow-lg shadow-gray-900/20">
                         <span className="text-sm">👤</span>
                       </div>
                     )}
                   </div>
                 ))}
                 <div ref={messagesEndRef} />
               </div>

               {/* Input Form */}
               <form onSubmit={handleSubmit} className="flex gap-2" style={{ pointerEvents: 'auto' }}>
                 <Input
                   type="text"
                   value={input}
                   onChange={(e) => setInput(e.target.value)}
                   placeholder="Type your message..."
                   className="flex-1 bg-black border-gray-700/40 focus:border-gray-500/40 text-white placeholder-gray-400 rounded-lg px-3 py-2 text-sm shadow-lg shadow-gray-900/10 transition-all duration-300 focus:shadow-gray-500/20"
                 />
                 <Button
                   type="submit"
                   variant="primary"
                   disabled={loading || !input.trim()}
                   className="bg-transparent text-white px-4 py-2 rounded-lg shadow-lg transition-all duration-300 border border-gray-700/40 hover:scale-105 hover:shadow-gray-500/40 disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-none text-sm"
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
               {/* Run Analysis Button removed as requested */}
             </div>
           </div>
         </div>
       </div>
     </div>
   );
 };

export default ChatPage;
