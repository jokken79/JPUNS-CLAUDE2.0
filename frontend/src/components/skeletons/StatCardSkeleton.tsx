import React from 'react';

const StatCardSkeleton: React.FC = () => {
  return (
    <div className="relative overflow-hidden rounded-3xl border border-white/60 bg-white/70 p-6 shadow-xl shadow-slate-900/5">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-200/40 via-white to-slate-100/40" aria-hidden="true" />
      <div className="relative flex items-center justify-between gap-4">
        <div className="flex-1 space-y-3">
          <div className="h-3 w-24 rounded-full bg-slate-200/80 animate-pulse" />
          <div className="h-10 w-40 rounded-2xl bg-slate-200/80 animate-pulse" />
          <div className="h-3 w-28 rounded-full bg-slate-200/80 animate-pulse" />
        </div>
        <div className="h-14 w-14 rounded-2xl bg-slate-200/80 animate-pulse" />
      </div>
    </div>
  );
};

export const StatsGridSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
      {Array.from({ length: 8 }).map((_, index) => (
        <StatCardSkeleton key={index} />
      ))}
    </div>
  );
};

export default StatCardSkeleton;
