import React, { Suspense } from 'react';
import useDashboardData from '../hooks/useDashboardData';
import {
  StatsGridSkeleton,
  AlertSkeleton,
  ActivitySkeleton,
  FactoriesTableSkeleton,
} from '../components/skeletons';

const StatsGrid = React.lazy(() => import('../components/dashboard/StatsGrid'));
const Alerts = React.lazy(() => import('../components/dashboard/Alerts'));
const RecentActivities = React.lazy(() => import('../components/dashboard/RecentActivities'));
const TopFactories = React.lazy(() => import('../components/dashboard/TopFactories'));


const Dashboard: React.FC = () => {
  const { stats, alerts, recentActivities, topFactories, loading } = useDashboardData();

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="relative overflow-hidden rounded-3xl border border-white/60 bg-white/80 p-8 shadow-xl shadow-slate-900/5 backdrop-blur">
        <div className="absolute inset-y-0 right-0 hidden w-1/2 translate-x-1/4 rounded-l-full bg-gradient-to-br from-indigo-400/20 via-sky-300/20 to-emerald-300/20 blur-3xl md:block" aria-hidden="true" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-indigo-500">Insight Center</p>
            <h1 className="mt-3 text-4xl font-semibold text-slate-900 lg:text-5xl">ダッシュボード</h1>
            <p className="mt-4 max-w-2xl text-base text-slate-600">
              組織全体のパフォーマンス、重要アラート、最新動向をワンビューで把握。意思決定を加速させるエグゼクティブレベルの分析体験を提供します。
            </p>
          </div>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-3 rounded-2xl border border-white/70 bg-white/80 px-4 py-3 shadow-sm shadow-slate-900/5">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <div>
                <p className="text-xs font-semibold text-slate-500">システムステータス</p>
                <p className="text-sm font-semibold text-slate-900">稼働中 / リアルタイム更新</p>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-2xl border border-white/70 bg-white/80 px-4 py-3 shadow-sm shadow-slate-900/5">
              <span className="rounded-full bg-indigo-500/15 px-3 py-1 text-xs font-semibold text-indigo-600">HR Excellence</span>
              <div className="text-sm font-semibold text-slate-700">KPI最適化ビュー</div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Grid */}
      <Suspense fallback={<StatsGridSkeleton />}>
        {loading ? <StatsGridSkeleton /> : <StatsGrid stats={stats} />}
      </Suspense>


      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Alerts */}
        <Suspense fallback={<AlertSkeleton />}>
            {loading ? <AlertSkeleton /> : <Alerts alerts={alerts} />}
        </Suspense>

        {/* Recent Activities */}
        <Suspense fallback={<ActivitySkeleton />}>
            {loading ? <ActivitySkeleton /> : <RecentActivities recentActivities={recentActivities} />}
        </Suspense>
      </div>

      {/* Top Factories */}
      <Suspense fallback={<FactoriesTableSkeleton />}>
        {loading ? <FactoriesTableSkeleton /> : <TopFactories topFactories={topFactories} />}
      </Suspense>
    </div>
  );
};

export default Dashboard;
