import React from 'react';
import Navbar from '../components/common/Navbar';
import AuthForm from '../components/auth/AuthForm';

const SignupPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <AuthForm type="signup" />
    </div>
  );
};

export default SignupPage;