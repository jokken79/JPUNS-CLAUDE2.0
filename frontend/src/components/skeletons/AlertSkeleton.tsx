import React from 'react';

const AlertItemSkeleton: React.FC = () => (
  <div className="p-4 rounded-lg border-l-4 bg-gray-50 border-gray-200">
    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
    <div className="h-3 bg-gray-200 rounded w-3/4"></div>
  </div>
);

const AlertSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="h-6 bg-gray-300 rounded w-1/3"></div>
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
      </div>
      <div className="space-y-3">
        <AlertItemSkeleton />
        <AlertItemSkeleton />
        <AlertItemSkeleton />
      </div>
    </div>
  );
};

export default AlertSkeleton;
