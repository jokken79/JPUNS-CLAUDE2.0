import React from 'react';

const FactoriesTableSkeleton: React.FC = () => {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/60 bg-white/70 p-6 shadow-xl shadow-slate-900/5">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-100/60 via-white to-slate-200/50" aria-hidden="true" />
      <div className="relative space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-6 w-40 rounded-full bg-slate-200/80 animate-pulse" />
          <div className="h-4 w-24 rounded-full bg-slate-200/80 animate-pulse" />
        </div>
        <div className="overflow-hidden rounded-2xl border border-white/70">
          <table className="min-w-full text-left">
            <thead className="bg-slate-100/60">
              <tr>
                {Array.from({ length: 5 }).map((_, index) => (
                  <th key={index} className="px-6 py-4">
                    <div className="h-4 w-full rounded-full bg-slate-200/80 animate-pulse" />
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100/70 bg-white/70">
              {Array.from({ length: 3 }).map((_, row) => (
                <tr key={row}>
                  {Array.from({ length: 5 }).map((_, col) => (
                    <td key={col} className="px-6 py-4">
                      <div className="h-4 w-full rounded-full bg-slate-200/80 animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};

export default FactoriesTableSkeleton;
