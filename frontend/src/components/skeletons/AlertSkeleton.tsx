import React from 'react';

const AlertItemSkeleton: React.FC = () => (
  <div className="relative overflow-hidden rounded-2xl border border-white/70 bg-white/80 p-4 shadow-sm">
    <div className="absolute inset-0 bg-gradient-to-r from-slate-100 via-white to-slate-100/60" aria-hidden="true" />
    <div className="relative space-y-2">
      <div className="h-4 w-1/2 rounded-full bg-slate-200/80 animate-pulse" />
      <div className="h-3 w-3/4 rounded-full bg-slate-200/80 animate-pulse" />
    </div>
  </div>
);

const AlertSkeleton: React.FC = () => {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/60 bg-white/70 p-6 shadow-xl shadow-slate-900/5">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-100/70 via-white to-slate-200/50" aria-hidden="true" />
      <div className="relative space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-6 w-32 rounded-full bg-slate-200/80 animate-pulse" />
          <div className="h-4 w-24 rounded-full bg-slate-200/80 animate-pulse" />
        </div>
        <div className="space-y-3">
          <AlertItemSkeleton />
          <AlertItemSkeleton />
          <AlertItemSkeleton />
        </div>
      </div>
    </section>
  );
};

export default AlertSkeleton;
