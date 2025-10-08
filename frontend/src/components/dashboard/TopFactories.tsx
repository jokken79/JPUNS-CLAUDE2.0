import React from 'react';
import { Factory } from '../../hooks/useDashboardData';
import { ArrowTrendingUpIcon } from '@heroicons/react/24/outline';

interface TopFactoriesProps {
  topFactories: Factory[];
}

const TopFactories: React.FC<TopFactoriesProps> = ({ topFactories }) => {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/60 bg-white/80 p-6 shadow-xl shadow-slate-900/5 backdrop-blur">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/15 text-emerald-600">
            <ArrowTrendingUpIcon className="h-6 w-6" />
          </span>
          <div>
            <h2 className="text-xl font-semibold text-slate-900">利益率上位の企業</h2>
            <p className="text-sm text-slate-600">パフォーマンスの高い企業をリアルタイムに把握</p>
          </div>
        </div>
        <button className="rounded-full border border-transparent bg-slate-900/5 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-900/10 hover:bg-slate-900/10">
          すべての企業を表示
        </button>
      </div>
      <div className="mt-6 overflow-x-auto">
        <table className="min-w-full overflow-hidden rounded-2xl border border-white/70 text-left shadow-sm">
          <thead className="bg-gradient-to-r from-slate-100 via-white to-slate-100/60 text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">
            <tr>
              <th className="px-6 py-4">企業ID</th>
              <th className="px-6 py-4">企業名</th>
              <th className="px-6 py-4">後継技能者数</th>
              <th className="px-6 py-4">先月比利益</th>
              <th className="px-6 py-4">利益率</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100/70 bg-white/80 text-sm text-slate-700">
            {topFactories.map((factory) => (
              <tr key={factory.id} className="transition hover:bg-indigo-50/60">
                <td className="px-6 py-4 font-semibold text-slate-900">{factory.id}</td>
                <td className="px-6 py-4">
                  <div className="flex flex-col">
                    <span className="font-medium text-slate-900">{factory.name}</span>
                    <span className="text-xs text-slate-500">トップパフォーマンス企業</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-slate-600">{factory.employees}名</td>
                <td className="px-6 py-4 text-emerald-600">
                  <span className="font-semibold">{factory.profit}</span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <span className="inline-flex min-w-[3rem] items-center justify-center rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-600">
                      {factory.margin}%
                    </span>
                    <div className="h-2 flex-1 rounded-full bg-slate-200">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-emerald-500 to-teal-500"
                        style={{ width: `${Math.min(factory.margin, 100)}%` }}
                      />
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

export default TopFactories;
