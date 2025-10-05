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
      name: '蛟呵｣懆・ｷ乗焚',
      value: '150',
      change: '+12',
      changeType: 'increase',
      icon: UserGroupIcon,
      color: 'bg-blue-500'
    },
    {
      name: '謇ｿ隱榊ｾ・■',
      value: '12',
      change: '+3',
      changeType: 'increase',
      icon: DocumentCheckIcon,
      color: 'bg-yellow-500'
    },
    {
      name: '蠕捺･ｭ蜩｡邱乗焚',
      value: '320',
      change: '+8',
      changeType: 'increase',
      icon: UserGroupIcon,
      color: 'bg-green-500'
    },
    {
      name: '遞ｼ蜒堺ｸｭ蠕捺･ｭ蜩｡',
      value: '305',
      change: '-2',
      changeType: 'decrease',
      icon: UserGroupIcon,
      color: 'bg-emerald-500'
    },
    {
      name: '蟾･蝣ｴ謨ｰ',
      value: '20',
      change: '0',
      changeType: 'neutral',
      icon: BuildingOfficeIcon,
      color: 'bg-purple-500'
    },
    {
      name: '謇ｿ隱榊ｾ・■逕ｳ隲・,
      value: '8',
      change: '+2',
      changeType: 'increase',
      icon: ClockIcon,
      color: 'bg-orange-500'
    },
    {
      name: '莉頑怦邨ｦ荳守ｷ城｡・,
      value: 'ﾂ･45,000,000',
      change: '+5.2%',
      changeType: 'increase',
      icon: CurrencyYenIcon,
      color: 'bg-green-600'
    },
    {
      name: '莉頑怦蛻ｩ逶・,
      value: 'ﾂ･8,500,000',
      change: '+3.8%',
      changeType: 'increase',
      icon: ArrowTrendingUpIcon,
      color: 'bg-indigo-500'
    }
  ];

  const alerts = [
    {
      id: 1,
      employee: '螻ｱ逕ｰ螟ｪ驛・,
      type: '蝨ｨ逡吶き繝ｼ繝画悄髯仙・繧・,
      daysUntil: 28,
      severity: 'warning'
    },
    {
      id: 2,
      employee: '菴占陸闃ｱ蟄・,
      type: '譛臥ｵｦ谿区律謨ｰ荳崎ｶｳ',
      remaining: 2,
      severity: 'info'
    },
    {
      id: 3,
      employee: '逕ｰ荳ｭ荳驛・,
      type: '螂醍ｴ・峩譁ｰ莠亥ｮ・,
      daysUntil: 45,
      severity: 'info'
    }
  ];

  const recentActivities = [
    {
      id: 1,
      type: '蛟呵｣懆・匳骭ｲ',
      description: '譁ｰ隕丞呵｣懆・碁斡譛ｨ蛛･螟ｪ縲阪ｒ逋ｻ骭ｲ縺励∪縺励◆',
      time: '5蛻・燕',
      user: '邂｡逅・・
    },
    {
      id: 2,
      type: '邨ｦ荳手ｨ育ｮ・,
      description: '2025蟷ｴ3譛亥・縺ｮ邨ｦ荳手ｨ育ｮ励′螳御ｺ・＠縺ｾ縺励◆',
      time: '1譎る俣蜑・,
      user: '繧ｷ繧ｹ繝・Β'
    },
    {
      id: 3,
      type: '逕ｳ隲区価隱・,
      description: '譛臥ｵｦ莨第嚊逕ｳ隲九ｒ謇ｿ隱阪＠縺ｾ縺励◆・亥ｱｱ逕ｰ螟ｪ驛趣ｼ・,
      time: '2譎る俣蜑・,
      user: '邂｡逅・・
    },
    {
      id: 4,
      type: '繧ｿ繧､繝繧ｫ繝ｼ繝・,
      description: 'Factory-01縺ｮ繧ｿ繧､繝繧ｫ繝ｼ繝峨ｒ繧｢繝・・繝ｭ繝ｼ繝峨＠縺ｾ縺励◆',
      time: '3譎る俣蜑・,
      user: '繧ｳ繝ｼ繝・ぅ繝阪・繧ｿ繝ｼ'
    }
  ];

  const topFactories = [
    {
      id: 'Factory-01',
      name: 'Toyota Aichi Factory',
      employees: 45,
      profit: 'ﾂ･950,000',
      margin: 18.5
    },
    {
      id: 'Factory-02',
      name: 'Honda Suzuka Factory',
      employees: 38,
      profit: 'ﾂ･820,000',
      margin: 17.2
    },
    {
      id: 'Factory-03',
      name: 'Nissan Yokohama',
      employees: 42,
      profit: 'ﾂ･780,000',
      margin: 16.8
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">繝繝・す繝･繝懊・繝・/h1>
        <p className="mt-2 text-gray-600">繧ｷ繧ｹ繝・Β縺ｮ讎りｦ√→譛霑代・繧｢繧ｯ繝・ぅ繝薙ユ繧｣</p>
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
                  {stat.change} 莉頑怦
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
              繧｢繝ｩ繝ｼ繝・            </h2>
            <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              縺吶∋縺ｦ陦ｨ遉ｺ
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
                    縺ゅ→{alert.daysUntil}譌･
                  </p>
                )}
                {'remaining' in alert && (
                  <p className="text-sm text-gray-500 mt-1">
                    谿九ｊ{alert.remaining}譌･
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
              譛霑代・繧｢繧ｯ繝・ぅ繝薙ユ繧｣
            </h2>
            <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              縺吶∋縺ｦ陦ｨ遉ｺ
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
                    {activity.time} 窶｢ {activity.user}
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
            蛻ｩ逶贋ｸ贋ｽ阪・蟾･蝣ｴ
          </h2>
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            縺吶∋縺ｦ縺ｮ蟾･蝣ｴ繧定｡ｨ遉ｺ
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  蟾･蝣ｴID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  蟾･蝣ｴ蜷・                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  蠕捺･ｭ蜩｡謨ｰ
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  莉頑怦蛻ｩ逶・                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  蛻ｩ逶顔紫
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
                    {factory.employees}蜷・                  </td>
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
