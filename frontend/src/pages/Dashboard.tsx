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
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">ダッシュボード</h1>
        <p className="mt-2 text-gray-600">システムの概要と最新のアクティビティ</p>
      </div>

      {/* Stats Grid */}
      <Suspense fallback={<StatsGridSkeleton />}>
        {loading ? <StatsGridSkeleton /> : <StatsGrid stats={stats} />}
      </Suspense>


      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
