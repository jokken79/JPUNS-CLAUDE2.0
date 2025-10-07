import React from 'react';

const ActivityItemSkeleton: React.FC = () => (
  <div className="flex items-start space-x-3">
    <div className="flex-shrink-0 w-2 h-2 mt-2 bg-gray-200 rounded-full"></div>
    <div className="flex-1 min-w-0">
      <div className="h-4 bg-gray-300 rounded w-1/4 mb-2"></div>
      <div className="h-3 bg-gray-200 rounded w-3/4 mb-2"></div>
      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
    </div>
  </div>
);

const ActivitySkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="h-6 bg-gray-300 rounded w-1/3"></div>
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
      </div>
      <div className="space-y-4">
        <ActivityItemSkeleton />
        <ActivityItemSkeleton />
        <ActivityItemSkeleton />
        <ActivityItemSkeleton />
      </div>
    </div>
  );
};

export default ActivitySkeleton;
