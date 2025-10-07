import React from 'react';
import { Alert } from '../../hooks/useDashboardData';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface AlertsProps {
  alerts: Alert[];
}

const Alerts: React.FC<AlertsProps> = ({ alerts }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900 flex items-center">
          <ExclamationTriangleIcon className="h-6 w-6 mr-2 text-yellow-500" />
          アラート
        </h2>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          すべて表示
        </button>
      </div>
      <div className="space-y-3">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={`p-4 rounded-lg border-l-4 ${
              alert.severity === 'warning'
                ? 'bg-yellow-50 border-yellow-400'
                : 'bg-blue-50 border-blue-400'
            }`}
          >
            <p className="font-medium text-gray-900">{alert.employee}</p>
            <p className="text-sm text-gray-600 mt-1">{alert.type}</p>
            {'daysUntil' in alert && (
              <p className="text-sm text-gray-500 mt-1">
                あと{alert.daysUntil}日
              </p>
            )}
            {'remaining' in alert && (
              <p className="text-sm text-gray-500 mt-1">
                残り{alert.remaining}日
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Alerts;
