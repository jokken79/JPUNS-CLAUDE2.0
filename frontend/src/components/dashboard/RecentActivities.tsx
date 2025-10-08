import React from 'react';
import { Activity } from '../../hooks/useDashboardData';
import { ChartBarIcon } from '@heroicons/react/24/outline';

interface RecentActivitiesProps {
  recentActivities: Activity[];
}

const RecentActivities: React.FC<RecentActivitiesProps> = ({ recentActivities }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900 flex items-center">
          <ChartBarIcon className="h-6 w-6 mr-2 text-primary-500" />
          最新のアクティビティ
        </h2>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          すべて表示
        </button>
      </div>
      <div className="space-y-4">
        {recentActivities.map((activity) => (
          <div key={activity.id} className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-2 h-2 mt-2 bg-primary-500 rounded-full"></div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">
                {activity.type}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {activity.description}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {activity.time} • {activity.user}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentActivities;
