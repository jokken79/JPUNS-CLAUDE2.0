import React from 'react';

const FactoriesTableSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="h-6 bg-gray-300 rounded w-1/3"></div>
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-6 py-3"><div className="h-4 bg-gray-200 rounded w-full"></div></th>
              <th className="px-6 py-3"><div className="h-4 bg-gray-200 rounded w-full"></div></th>
              <th className="px-6 py-3"><div className="h-4 bg-gray-200 rounded w-full"></div></th>
              <th className="px-6 py-3"><div className="h-4 bg-gray-200 rounded w-full"></div></th>
              <th className="px-6 py-3"><div className="h-4 bg-gray-200 rounded w-full"></div></th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {[...Array(3)].map((_, i) => (
              <tr key={i}>
                <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-full"></div></td>
                <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-full"></div></td>
                <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-full"></div></td>
                <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-full"></div></td>
                <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-full"></div></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FactoriesTableSkeleton;
