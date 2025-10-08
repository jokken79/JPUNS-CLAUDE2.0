import React from 'react';

const ActivityItemSkeleton: React.FC = () => (
  <div className="relative flex gap-4 pl-14">
    <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-2xl border border-white/70 bg-white/80 shadow-sm">
      <div className="h-4 w-4 rounded-full bg-slate-200/80 animate-pulse" />
    </div>
    <div className="flex-1 space-y-2">
      <div className="h-4 w-1/3 rounded-full bg-slate-200/80 animate-pulse" />
      <div className="h-3 w-3/4 rounded-full bg-slate-200/80 animate-pulse" />
      <div className="h-3 w-1/2 rounded-full bg-slate-200/70 animate-pulse" />
    </div>
  </div>
);

const ActivitySkeleton: React.FC = () => {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/60 bg-white/70 p-6 shadow-xl shadow-slate-900/5">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-100/60 via-white to-slate-200/50" aria-hidden="true" />
      <div className="relative space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-6 w-40 rounded-full bg-slate-200/80 animate-pulse" />
          <div className="h-4 w-24 rounded-full bg-slate-200/80 animate-pulse" />
        </div>
        <div className="relative">
          <div className="absolute left-[1.4rem] top-0 bottom-0 w-px bg-slate-200/60" aria-hidden="true" />
          <div className="space-y-6">
            <ActivityItemSkeleton />
            <ActivityItemSkeleton />
            <ActivityItemSkeleton />
            <ActivityItemSkeleton />
          </div>
        </div>
      </div>
    </section>
  );
};

export default ActivitySkeleton;
