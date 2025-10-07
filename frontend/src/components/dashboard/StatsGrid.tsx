import React from 'react';
import { Stat } from '../../hooks/useDashboardData';

interface StatsGridProps {
  stats: Stat[];
}

const StatsGrid: React.FC<StatsGridProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => (
        <div
          key={stat.name}
          className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition"
        >
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">{stat.name}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
              <p
                className={`mt-2 text-sm font-medium ${
                  stat.changeType === 'increase'
                    ? 'text-green-600'
                    : stat.changeType === 'decrease'
                    ? 'text-red-600'
                    : 'text-gray-600'
                }`}
              >
                {stat.change} 先月比
              </p>
            </div>
            <div className={`${stat.color} rounded-xl p-3`}>
              <stat.icon className="h-8 w-8 text-white" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatsGrid;
