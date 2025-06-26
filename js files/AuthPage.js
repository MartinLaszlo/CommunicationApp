import React, { useState } from 'react';
import axios from 'axios';

const AuthPage = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginType, setLoginType] = useState('student'); // 'student' or 'staff'

  const handleUsernameChange = (e) => setUsername(e.target.value);
  const handlePasswordChange = (e) => setPassword(e.target.value);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const loginEndpoint = loginType === 'student' ? '/login/student' : '/login/staff';

    try {
      const response = await axios.post(`http://localhost:5000${loginEndpoint}`, {
        username,
        password,
      });
      if (response.data.success) {
        // Store user info including ID
        localStorage.setItem('user', JSON.stringify({
          user_ID: response.data.user_ID, // user_ID for direct messaging
          id: response.data.id, // id for group messaging
          name: response.data.name,
          program_ID: response.data.program_ID,
          role: response.data.role // 'student' or 'staff'
        }));
        onLoginSuccess();
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed: ' + error.response?.data?.message || error.message);
    }
  };

  const toggleLoginType = () => setLoginType(prevType => prevType === 'student' ? 'staff' : 'student');
  // Authentication window
  return (
    <div className="flex justify-center items-center h-screen" style={{ background: 'linear-gradient(to bottom, #172442, #090f1c)' }}>
      <div className="w-full max-w-xs">
        <form onSubmit={handleSubmit} className="bg-white shadow-2xl rounded-3xl px-8 pt-6 pb-8 mb-4">
          <div className="mb-4 text-center">
          </div>
          <div className="mb-4">
            <label htmlFor="username" className="block text-gray-700 text-lg font-bold mb-2">
              Username:
            </label>
            <input
              type="text"
              id="username"
              value={username}
              placeholder="Username"
              onChange={handleUsernameChange}
              className="shadow appearance-none border rounded-3xl w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
            />
          </div>
          <div className="mb-6">
            <label htmlFor="password" className="block text-gray-700 text-lg font-bold mb-2">
              Password:
            </label>
            <input
              type="password"
              id="password"
              value={password}
              placeholder="Password"
              onChange={handlePasswordChange}
              className="shadow appearance-none border rounded-3xl w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
              required
            />
          </div>
          <div className="flex items-center justify-between">
            <button
              type="submit"
              className="bg-gradient-to-r from-blue-600 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none  text-white font-bold py-2 px-4 rounded-3xl focus:outline-none focus:shadow-outline text-base flex-grow transition duration-300 ease-in-out"
            >
              Log in as {loginType}
            </button>
            <button
              type="button"
              onClick={toggleLoginType}
              className="ml-4 bg-gradient-to-r from-blue-600 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none text-white font-bold py-2 px-4 rounded-3xl focus:outline-none focus:shadow-outline text-base transition duration-300 ease-in-out"
            >
              Switch to {loginType === 'student' ? 'Staff' : 'Student'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AuthPage;
