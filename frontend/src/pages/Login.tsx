import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { LockClosedIcon, UserIcon } from '@heroicons/react/24/outline';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params.toString(),
      });

      if (!response.ok) {
        const data = await response.json();
        toast.error(data.detail || 'ユーザー名またはパスワードが正しくありません');
        setLoading(false);
        return;
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      toast.success('ログインに成功しました');
      navigate('/dashboard');
    } catch (error) {
      toast.error('ログインエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Floating Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-32 w-96 h-96 bg-indigo-300/30 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-1/4 -right-20 w-72 h-72 bg-purple-300/30 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute -bottom-32 left-1/3 w-80 h-80 bg-pink-300/30 rounded-full blur-3xl animate-pulse delay-2000" />
      </div>

      <div className="relative max-w-md w-full">
        {/* Floating Logo Circle */}
        <div className="flex justify-center mb-12">
          <div className="relative group">
            <div className="absolute -inset-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full blur-lg opacity-75 group-hover:opacity-100 transition duration-1000 animate-pulse" />
            <div className="relative w-32 h-32 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-2xl transform transition-all duration-500 hover:scale-110 hover:rotate-12">
              <span className="text-white text-4xl font-black tracking-wider">UNS</span>
            </div>
          </div>
        </div>

        {/* Title */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 mb-2">
            UNS-ClaudeJP 2.0
          </h1>
          <p className="text-gray-600 font-medium">
            人材管理インテリジェンスプラットフォーム
          </p>
        </div>

        {/* Floating Login Card */}
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-500" />
          <div className="relative bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/50">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 text-center">
                ログイン
              </h2>
              <p className="text-center text-gray-600 mt-2 text-sm">
                アカウント情報を入力してください
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Username */}
              <div className="space-y-2">
                <label htmlFor="username" className="block text-sm font-semibold text-gray-700">
                  ユーザー名
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <UserIcon className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition" />
                  </div>
                  <input
                    id="username"
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="block w-full pl-12 pr-4 py-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent focus:bg-white transition-all duration-200 placeholder-gray-400"
                    placeholder="ユーザー名を入力"
                    autoComplete="username"
                  />
                </div>
              </div>

              {/* Password */}
              <div className="space-y-2">
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700">
                  パスワード
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <LockClosedIcon className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition" />
                  </div>
                  <input
                    id="password"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="block w-full pl-12 pr-4 py-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent focus:bg-white transition-all duration-200 placeholder-gray-400"
                    placeholder="パスワードを入力"
                    autoComplete="current-password"
                  />
                </div>
              </div>

              {/* Remember Me & Forgot Password */}
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-gray-700 font-medium">
                    ログイン状態を保持
                  </label>
                </div>
                <a href="#" className="font-semibold text-indigo-600 hover:text-indigo-500 transition">
                  パスワードを忘れた場合
                </a>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className={`relative w-full group overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 p-0.5 transition-all duration-300 ${
                  loading ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-lg hover:shadow-indigo-500/50'
                }`}
              >
                <div className="relative flex justify-center items-center py-3.5 px-4 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-xl group-hover:from-indigo-600 group-hover:via-purple-600 group-hover:to-pink-600 transition-all duration-300">
                  {loading ? (
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <span className="text-white font-bold text-base">ログイン</span>
                  )}
                </div>
              </button>
            </form>

            {/* Demo Credentials */}
            <div className="mt-8 p-4 bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200/50 rounded-2xl">
              <p className="text-sm text-amber-900 font-bold mb-2 flex items-center gap-2">
                <svg className="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                デモアカウント
              </p>
              <div className="space-y-1">
                <p className="text-xs text-amber-800 font-medium">
                  ユーザー名: <span className="font-mono font-bold text-amber-900">admin</span>
                </p>
                <p className="text-xs text-amber-800 font-medium">
                  パスワード: <span className="font-mono font-bold text-amber-900">admin123</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600 font-medium">
            © 2025 UNS企画. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
