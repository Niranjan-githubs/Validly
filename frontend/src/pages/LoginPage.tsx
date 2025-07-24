import React from 'react';
import Navbar from '../components/common/Navbar';
import AuthForm from '../components/auth/AuthForm';

const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <AuthForm type="login" />
    </div>
  );
};

export default LoginPage;