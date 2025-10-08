import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  ClockIcon,
  CurrencyYenIcon,
  DocumentTextIcon,
  UserPlusIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowUpTrayIcon
} from '@heroicons/react/24/outline';

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  const navigation = [
    { name: 'ダッシュボード', href: '/dashboard', icon: HomeIcon },
    { name: '履歴書管理', href: '/candidates', icon: UserPlusIcon },
    { name: '従業員管理', href: '/employees', icon: UserGroupIcon },
    { name: '従業員管理（詳細）', href: '/employees-extended', icon: UserGroupIcon },
    { name: 'データインポート', href: '/import-data', icon: ArrowUpTrayIcon },
    { name: '企業管理', href: '/factories', icon: BuildingOfficeIcon },
    { name: 'タイムカード', href: '/timer-cards', icon: ClockIcon },
    { name: '給与計算', href: '/salary', icon: CurrencyYenIcon },
    { name: '申請管理', href: '/requests', icon: DocumentTextIcon },
  ];

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-100 via-white to-indigo-100">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-32 -top-40 h-72 w-72 rounded-full bg-indigo-300/40 blur-3xl" />
        <div className="absolute right-[-18%] top-1/3 h-[28rem] w-[28rem] rounded-full bg-violet-300/35 blur-[120px]" />
        <div className="absolute bottom-[-20%] left-1/4 h-96 w-96 rounded-full bg-emerald-200/40 blur-[120px]" />
      </div>

      {/* Top Navigation */}
      <nav className="fixed inset-x-0 top-0 z-40 px-4 pt-4 sm:px-6 lg:px-10">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between rounded-2xl border border-white/60 bg-white/80 px-4 shadow-lg shadow-slate-900/10 backdrop-blur">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              aria-label={sidebarOpen ? 'サイドバーを閉じる' : 'サイドバーを開く'}
              className="flex h-11 w-11 items-center justify-center rounded-xl border border-white/70 bg-white/80 text-slate-500 transition hover:border-indigo-200 hover:text-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:ring-offset-2 focus:ring-offset-white"
            >
              {sidebarOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 via-sky-500 to-emerald-500 text-white shadow-lg shadow-indigo-500/20">
                <span className="text-lg font-bold">UNS</span>
              </div>
              <div>
                <p className="text-lg font-semibold text-slate-900">UNS-ClaudeJP 2.0</p>
                <p className="text-xs text-slate-500">人材管理インテリジェンスプラットフォーム</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden text-right sm:flex sm:flex-col">
              <span className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">ログイン中</span>
              <span className="text-sm font-semibold text-slate-700">管理者</span>
            </div>
            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-rose-500 via-orange-500 to-amber-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-rose-500/20 transition hover:shadow-rose-500/40 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 focus:ring-offset-white"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
              ログアウト
            </button>
          </div>
        </div>
      </nav>

      {/* Sidebar & Main */}
      <div className="relative z-10 flex pt-28">
        <div
          className={`${sidebarOpen ? 'w-72' : 'w-0'} transition-all duration-500 ease-in-out`}
        >
          <aside
            className={`pointer-events-auto fixed top-24 bottom-8 left-4 right-auto z-30 flex h-[calc(100vh-7.5rem)] w-72 flex-col overflow-hidden rounded-3xl border border-white/60 bg-white/80 p-4 shadow-2xl shadow-slate-900/10 backdrop-blur transition-transform duration-500 ease-[cubic-bezier(0.4,0,0.2,1)] ${
              sidebarOpen ? 'translate-x-0 opacity-100' : '-translate-x-[120%] opacity-0'
            } sm:left-6 lg:left-10`}
          >
            <div className="flex items-center justify-between pb-4">
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">Navigation</p>
              <span className="rounded-full bg-slate-900/5 px-3 py-1 text-[0.65rem] font-semibold text-slate-500">HR Suite</span>
            </div>
            <nav className="flex flex-1 flex-col gap-2 overflow-y-auto pr-1">
              {navigation.map((item) => {
                const isActive =
                  location.pathname === item.href || location.pathname.startsWith(item.href + '/');
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`group relative flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold transition-all duration-300 ${
                      isActive
                        ? 'bg-gradient-to-r from-indigo-500/15 via-sky-500/10 to-indigo-500/15 text-indigo-600 shadow-lg shadow-indigo-500/20 ring-1 ring-indigo-200/60'
                        : 'text-slate-600 hover:bg-white/70 hover:text-slate-900 hover:shadow-sm'
                    }`}
                  >
                    <span
                      className={`flex h-10 w-10 items-center justify-center rounded-xl border ${
                        isActive
                          ? 'border-indigo-300 bg-white text-indigo-500'
                          : 'border-white/70 bg-white/80 text-slate-500 group-hover:border-indigo-200 group-hover:text-indigo-500'
                      }`}
                    >
                      <item.icon className="h-5 w-5" />
                    </span>
                    <span className="truncate">{item.name}</span>
                    {isActive && (
                      <span className="absolute inset-y-1 left-1 w-1 rounded-full bg-indigo-500" aria-hidden="true" />
                    )}
                  </Link>
                );
              })}
            </nav>
            <div className="mt-6 rounded-2xl border border-dashed border-slate-200/80 bg-slate-50/80 p-4 text-xs font-medium text-slate-500">
              卓越した人材エクスペリエンスを実現するためのインサイトを提供します。
            </div>
          </aside>
        </div>

        <main
          className={`flex-1 px-4 pb-12 transition-all duration-500 sm:px-6 lg:px-10 ${
            sidebarOpen ? 'md:ml-[19rem]' : 'md:ml-20'
          }`}
        >
          <div className="mx-auto w-full max-w-7xl space-y-10">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
