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
import VCInvestorCardDetails from '../components/newDashboard/VCInvestorCardDetails';
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
        path="/new-dashboard/CompetitorIntelligence"
        element={
          <ProtectedRoute>
            <CompetitorIntelligence />
          </ProtectedRoute>
        }
      />
      <Route
        path="/new-dashboard/userpainpointDetails"
        element={
          <ProtectedRoute>
            <UserPainpointDetails />
          </ProtectedRoute>
        }
      />
      <Route
        path="/new-dashboard/VCInvestorCardDetails"
        element={
          <ProtectedRoute>
            <VCInvestorCardDetails />
          </ProtectedRoute>
        }
      />
      <Route
        path="/new-dashboard/MarketAnalysisDetail"
        element={
          <ProtectedRoute>
            <MarketAnalysisDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/new-dashboard/RiskAssessmentDetail"
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