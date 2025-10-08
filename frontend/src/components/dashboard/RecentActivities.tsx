import React from 'react';
import { Activity } from '../../hooks/useDashboardData';
import { ChartBarIcon } from '@heroicons/react/24/outline';

interface RecentActivitiesProps {
  recentActivities: Activity[];
}

const RecentActivities: React.FC<RecentActivitiesProps> = ({ recentActivities }) => {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/60 bg-white/80 p-6 shadow-xl shadow-slate-900/5 backdrop-blur">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-500/15 text-indigo-600">
            <ChartBarIcon className="h-6 w-6" />
          </span>
          <div>
            <h2 className="text-xl font-semibold text-slate-900">最新のアクティビティ</h2>
            <p className="text-sm text-slate-600">チームの更新状況と重要なトランザクションを追跡</p>
          </div>
        </div>
        <button className="rounded-full border border-transparent bg-slate-900/5 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-900/10 hover:bg-slate-900/10">
          すべて表示
        </button>
      </div>
      <div className="relative mt-6">
        <div className="absolute left-[1.4rem] top-0 bottom-0 w-px bg-gradient-to-b from-indigo-200 via-slate-200 to-transparent" aria-hidden="true" />
        <div className="space-y-6">
          {recentActivities.map((activity, index) => (
            <article key={activity.id} className="relative flex gap-4 pl-14">
              <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-2xl border border-white/70 bg-white text-indigo-600 shadow-sm shadow-slate-900/10">
                <span className="text-sm font-semibold">{String(index + 1).padStart(2, '0')}</span>
              </div>
              <div className="flex-1 space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-base font-semibold text-slate-900">{activity.type}</p>
                  <span className="rounded-full bg-indigo-500/10 px-3 py-1 text-xs font-semibold text-indigo-600">
                    {activity.time}
                  </span>
                </div>
                <p className="text-sm text-slate-700">{activity.description}</p>
                <p className="text-xs font-medium text-slate-500">更新者: {activity.user}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default RecentActivities;
