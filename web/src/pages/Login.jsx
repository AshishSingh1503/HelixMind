import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';
import { LogIn } from 'lucide-react';

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    console.log('🔐 Login: Attempting login with:', formData.username);

    try {
      console.log('📤 Login: Calling API...');
      const response = await authAPI.login(formData);
      console.log('✅ Login: Response received:', response);
      
      const { access_token } = response.data;
      console.log('🎫 Login: Token received:', access_token ? 'Yes' : 'No');
      
      localStorage.setItem('token', access_token);
      console.log('💾 Login: Token saved to localStorage');
      
      // Get user profile
      console.log('👤 Login: Fetching user profile...');
      const profileResponse = await authAPI.getProfile();
      console.log('✅ Login: Profile received:', profileResponse.data);
      
      onLogin(profileResponse.data);
      
      toast.success('Login successful!');
      navigate('/dashboard');
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('❌ Login error response:', error.response);
      console.error('❌ Login error data:', error.response?.data);
      toast.error(error.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <LogIn className="mx-auto h-12 w-12 text-primary-600" />
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Sign in to GenomeGuard
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Or{' '}
            <Link to="/register" className="text-primary-600 hover:text-primary-500">
              create a new account
            </Link>
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              required
              className="input-field mt-1"
              placeholder="Enter your username"
              value={formData.username}
              onChange={handleChange}
            />
          </div>
          
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="input-field mt-1"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;