import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LandingPage from '../pages/LandingPage';
import LoginPage from '../pages/LoginPage';
import SignupPage from '../pages/SignupPage';
import ChatPage from '../pages/ChatPage';
import DashboardPage from '../pages/DashboardPage';
import CompetitorIntelligence from '../components/newDashboard/CompetitorIntelligence';
import UserPainpointDetails from '../components/newDashboard/userpainpointDetails';
// import VCInvestorCardDetails from '../components/newDashboard/VCInvestorCardDetails';
import MarketAnalysisDetail from '../components/newDashboard/MarketAnalysisDetail';
import RiskAssessmentDetail from '../components/newDashboard/RiskAssessmentDetail';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
};

const AppRoutes: React.FC = () => {
  return (
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
            <DashboardPage />
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
        path="/new-dashboard/userpainpointDetails/:sessionId"
        element={
          <ProtectedRoute>
            <UserPainpointDetails />
          </ProtectedRoute>
        }
      />
      {/* Removed duplicate VCInvestorCardDetails route. Use the /new-dashboard/agent/VCInvestorCardDetails/:sessionId route defined in App.tsx */}
      <Route
        path="/new-dashboard/MarketAnalysisDetail"
        element={
          <ProtectedRoute>
            <MarketAnalysisDetail />
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
  );
};

export default AppRoutes; 