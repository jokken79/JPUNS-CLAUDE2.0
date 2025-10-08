import React from 'react';
import { Alert } from '../../hooks/useDashboardData';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface AlertsProps {
  alerts: Alert[];
}

const Alerts: React.FC<AlertsProps> = ({ alerts }) => {
  const severityStyles = {
    warning: {
      accent: 'from-amber-400/20 via-amber-300/10 to-yellow-300/20',
      badge: 'bg-amber-500/15 text-amber-700',
      label: '優先度: 高',
      border: 'bg-amber-400/80',
    },
    info: {
      accent: 'from-sky-400/20 via-blue-300/10 to-indigo-300/20',
      badge: 'bg-indigo-500/15 text-indigo-700',
      label: '優先度: 中',
      border: 'bg-indigo-400/80',
    },
  } as const;

  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/60 bg-white/80 p-6 shadow-xl shadow-slate-900/5 backdrop-blur">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-400/15 text-amber-600">
            <ExclamationTriangleIcon className="h-6 w-6" />
          </span>
          <div>
            <h2 className="text-xl font-semibold text-slate-900">アラート</h2>
            <p className="text-sm text-slate-600">重要な期限とフォローアップを見逃さないように管理</p>
          </div>
        </div>
        <button className="rounded-full border border-transparent bg-slate-900/5 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-900/10 hover:bg-slate-900/10">
          すべて表示
        </button>
      </div>
      <div className="mt-6 space-y-4">
        {alerts.map((alert) => {
          const severity = severityStyles[alert.severity];

          return (
            <article
              key={alert.id}
              className="relative overflow-hidden rounded-2xl border border-white/70 bg-white/80 p-4 shadow-sm shadow-slate-900/5 transition hover:shadow-lg"
            >
              <div className={`absolute inset-0 opacity-80 bg-gradient-to-r ${severity.accent}`} />
              <div className="relative flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <p className="text-base font-semibold text-slate-900">{alert.employee}</p>
                  <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${severity.badge}`}>
                    <span className={`h-2 w-2 rounded-full ${severity.border}`} />
                    {severity.label}
                  </span>
                </div>
                <p className="text-sm text-slate-700">{alert.type}</p>
                {'daysUntil' in alert && (
                  <p className="text-xs font-medium text-slate-600">
                    期限まであと <span className="font-semibold text-slate-900">{alert.daysUntil}日</span>
                  </p>
                )}
                {'remaining' in alert && (
                  <p className="text-xs font-medium text-slate-600">
                    残り日数 <span className="font-semibold text-slate-900">{alert.remaining}日</span>
                  </p>
                )}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
};

export default Alerts;
