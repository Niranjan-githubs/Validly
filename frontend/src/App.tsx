          <Route
            path="/new-dashboard/agent/userpainpointDetails/:sessionId"
            element={
              <ProtectedRoute>
                <UserPainpointDetails />
              </ProtectedRoute>
            }
          />
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
          {/* New Dashboard Session-Aware Routes */}
          <Route
            path="/new-dashboard"
            element={
              <ProtectedRoute>
                <NewDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/new-dashboard/agent/:agentName/:sessionId"
            element={
              <ProtectedRoute>
                <AgentDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/new-dashboard/agent/competitor_analysis/:sessionId"
            element={
              <ProtectedRoute>
                <CompetitorIntelligence />
              </ProtectedRoute>
            }
          />
          <Route
            path="/new-dashboard/agent/VCInvestorCardDetails/:sessionId"
            element={
              <ProtectedRoute>
                <VCInvestorCardDetails />
              </ProtectedRoute>
            }
          />
          <Route
            path="/new-dashboard/agent/MarketAnalysisDetail/:sessionId"
            element={
              <ProtectedRoute>
                <MarketAnalysisDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/new-dashboard/agent/userpainpointDetails/:sessionId"
            element={
              <ProtectedRoute>
                <UserPainpointDetails />
              </ProtectedRoute>
            }
          />
          <Route
            path="/new-dashboard/agent/RiskAssessmentDetail/:sessionId"
            element={
              <ProtectedRoute>
                <RiskAssessmentDetail />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;