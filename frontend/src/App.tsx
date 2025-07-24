import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ChatPage from './pages/ChatPage';
import DashboardPage from './pages/DashboardPage';
import NewDashboardPage from './pages/NewDashboardPage';
import AgentDetailPage from './pages/AgentDetailPage';
import CompetitorIntelligence from './components/newDashboard/CompetitorIntelligence';
import UserPainpointDetails from './components/newDashboard/userpainpointDetails';
import VCInvestorCardDetails from './components/newDashboard/VCInvestorCardDetails';
import MarketAnalysisDetail from './components/newDashboard/MarketAnalysisDetail';
import RiskAssessmentDetail from './components/newDashboard/RiskAssessmentDetail';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <NewDashboardPage />
              </ProtectedRoute>
            }
          />
          {/* New Dashboard Routes */}
          <Route path="/new-dashboard" element={<NewDashboardPage />} />
          <Route path="/new-dashboard/agent/:agentName" element={<AgentDetailPage />} />
          <Route path="/new-dashboard/CompetitorIntelligence" element={<CompetitorIntelligence />} />
          <Route path="/new-dashboard/userpainpointDetails" element={<UserPainpointDetails />} />
          <Route path="/new-dashboard/VCInvestorCardDetails" element={<VCInvestorCardDetails investor={{ name: '', amountInvested: '', differentiators: [], description: '', inspiration: '', stage: 'Seed', marketFocus: '' }} index={0} />} />
          <Route path="/new-dashboard/MarketAnalysisDetail" element={<MarketAnalysisDetail />} />
          <Route path="/new-dashboard/RiskAssessmentDetail" element={<RiskAssessmentDetail />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;