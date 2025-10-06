import React from 'react';
import {
  UserGroupIcon,
  BuildingOfficeIcon,
  ClockIcon,
  CurrencyYenIcon,
  DocumentCheckIcon,
  ExclamationTriangleIcon,
    ArrowTrendingUpIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  // Datos de ejemplo (luego vendrﾃ｡n de la API)
  const stats = [
    {
      name: '登録従業員数',
      value: '150',
      change: '+12',
      changeType: 'increase',
      icon: UserGroupIcon,
      color: 'bg-blue-500'
    },
    {
      name: '承認待ち',
      value: '12',
      change: '+3',
      changeType: 'increase',
      icon: DocumentCheckIcon,
      color: 'bg-yellow-500'
    },
    {
      name: '後継技能者数',
      value: '320',
      change: '+8',
      changeType: 'increase',
      icon: UserGroupIcon,
      color: 'bg-green-500'
    },
    {
      name: '派遣中後継技能者',
      value: '305',
      change: '-2',
      changeType: 'decrease',
      icon: UserGroupIcon,
      color: 'bg-emerald-500'
    },
    {
      name: '企業数',
      value: '20',
      change: '0',
      changeType: 'neutral',
      icon: BuildingOfficeIcon,
      color: 'bg-purple-500'
    },
    {
      name: '承認待ち申請',
      value: '8',
      change: '+2',
      changeType: 'increase',
      icon: ClockIcon,
      color: 'bg-orange-500'
    },
    {
      name: '今月給与支給額',
      value: '¥45,000,000',
      change: '+5.2%',
      changeType: 'increase',
      icon: CurrencyYenIcon,
      color: 'bg-green-600'
    },
    {
      name: '今月利益',
      value: '¥8,500,000',
      change: '+3.8%',
      changeType: 'increase',
      icon: ArrowTrendingUpIcon,
      color: 'bg-indigo-500'
    }
  ];

  const alerts = [
    {
      id: 1,
      employee: '山田太郎',
      type: '在留カード期限近づく',
      daysUntil: 28,
      severity: 'warning'
    },
    {
      id: 2,
      employee: '佐藤花子',
      type: '有給残日数不足',
      remaining: 2,
      severity: 'info'
    },
    {
      id: 3,
      employee: '田中三郎',
      type: '雇用契約更新必要',
      daysUntil: 45,
      severity: 'info'
    }
  ];

  const recentActivities = [
    {
      id: 1,
      type: '従業員登録',
      description: '新規従業員「佐藤花子」を登録しました',
      time: '5分前',
      user: '管理者'
    },
    {
      id: 2,
      type: '給与計算完了',
      description: '2025年3月分の給与計算が完了しました',
      time: '1時間前',
      user: 'システム'
    },
    {
      id: 3,
      type: '申請承認完了',
      description: '有給休暇申請を承認しました（山田太郎）',
      time: '2時間前',
      user: '管理者'
    },
    {
      id: 4,
      type: 'タイムカード',
      description: 'Factory-01のタイムカードをアップロードしました',
      time: '3時間前',
      user: 'コーディネーター'
    }
  ];

  const topFactories = [
    {
      id: 'Factory-01',
      name: 'Toyota Aichi Factory',
      employees: 45,
      profit: '¥950,000',
      margin: 18.5
    },
    {
      id: 'Factory-02',
      name: 'Honda Suzuka Factory',
      employees: 38,
      profit: '¥820,000',
      margin: 17.2
    },
    {
      id: 'Factory-03',
      name: 'Nissan Yokohama',
      employees: 42,
      profit: '¥780,000',
      margin: 16.8
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">ダッシュボード</h1>
        <p className="mt-2 text-gray-600">システムの概要と最新のアクティビティ</p>
      </div>

      {/* Stats Grid */}
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
                <p className={`mt-2 text-sm font-medium ${
                  stat.changeType === 'increase' ? 'text-green-600' :
                  stat.changeType === 'decrease' ? 'text-red-600' :
                  'text-gray-600'
                }`}>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alerts */}
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
                  alert.severity === 'warning' ? 'bg-yellow-50 border-yellow-400' :
                  'bg-blue-50 border-blue-400'
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

        {/* Recent Activities */}
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
      </div>

      {/* Top Factories */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 flex items-center">
            <ArrowTrendingUpIcon className="h-6 w-6 mr-2 text-green-500" />
            利益率上位の企業
          </h2>
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            すべての企業を表示
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  企業ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  企業名
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  後継技能者数
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  先月比利益
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  利益率
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {topFactories.map((factory) => (
                <tr key={factory.id} className="hover:bg-gray-50 cursor-pointer transition">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {factory.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {factory.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {factory.employees}名
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600">
                    {factory.profit}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {factory.margin}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
