import React from 'react';
import { Stat } from '../../hooks/useDashboardData';
import {
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  MinusSmallIcon,
} from '@heroicons/react/24/outline';

interface StatsGridProps {
  stats: Stat[];
}

const StatsGrid: React.FC<StatsGridProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => {
        const trendStyles =
          stat.changeType === 'increase'
            ? {
                icon: ArrowTrendingUpIcon,
                badge: 'bg-emerald-500/10 text-emerald-600',
                label: 'ポジティブな推移',
              }
            : stat.changeType === 'decrease'
            ? {
                icon: ArrowTrendingDownIcon,
                badge: 'bg-rose-500/10 text-rose-600',
                label: '注意が必要',
              }
            : {
                icon: MinusSmallIcon,
                badge: 'bg-slate-500/10 text-slate-600',
                label: '安定推移',
              };

        const TrendIcon = trendStyles.icon;

        return (
          <article
            key={stat.name}
            className="group relative overflow-hidden rounded-3xl border border-white/60 bg-white/80 p-6 shadow-xl shadow-slate-900/5 backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl"
          >
            <div
              className={`pointer-events-none absolute inset-0 opacity-80 transition-opacity duration-500 group-hover:opacity-100 bg-gradient-to-br ${stat.gradient}`}
            />
            <div className="relative flex h-full flex-col justify-between gap-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <span className="inline-flex items-center rounded-full bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600 shadow-sm">
                    {stat.name}
                  </span>
                  <p className="mt-4 text-4xl font-semibold leading-tight text-slate-900">
                    {stat.value}
                  </p>
                </div>
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-white/70 bg-white/80 shadow-inner shadow-white/40">
                  <stat.icon className="h-7 w-7 text-slate-700" />
                </div>
              </div>
              <div className="flex items-center justify-between text-sm font-semibold text-slate-700">
                <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${trendStyles.badge}`}>
                  <TrendIcon className="h-4 w-4" />
                  <span>{trendStyles.label}</span>
                </div>
                <p className="text-base font-semibold text-slate-800">
                  {stat.change}
                  <span className="ml-1 text-sm font-medium text-slate-600">先月比</span>
                </p>
              </div>
            </div>
            <div className="pointer-events-none absolute -bottom-16 -right-16 h-40 w-40 rounded-full bg-white/60 blur-3xl transition-transform duration-500 group-hover:translate-x-6 group-hover:-translate-y-4" />
          </article>
        );
      })}
    </div>
  );
};

export default StatsGrid;
