
import { useState, useEffect } from 'react';
import {
  UserGroupIcon,
  BuildingOfficeIcon,
  ClockIcon,
  CurrencyYenIcon,
  DocumentCheckIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';

// Interfaces para tipar los datos
export interface Stat {
  name: string;
  value: string;
  change: string;
  changeType: 'increase' | 'decrease' | 'neutral';
  icon: React.ElementType;
  gradient: string;
}

export interface Alert {
  id: number;
  employee: string;
  type: string;
  daysUntil?: number;
  remaining?: number;
  severity: 'warning' | 'info';
}

export interface Activity {
  id: number;
  type: string;
  description: string;
  time: string;
  user: string;
}

export interface Factory {
  id: string;
  name: string;
  employees: number;
  profit: string;
  margin: number;
}

const useDashboardData = () => {
  const [stats, setStats] = useState<Stat[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [recentActivities, setRecentActivities] = useState<Activity[]>([]);
  const [topFactories, setTopFactories] = useState<Factory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      // Simular un retardo de la API
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Datos de ejemplo
      setStats([
        {
          name: '登録従業員数',
          value: '150',
          change: '+12',
          changeType: 'increase',
          icon: UserGroupIcon,
          gradient: 'from-sky-400/90 via-blue-500/90 to-indigo-500/90'
        },
        {
          name: '承認待ち',
          value: '12',
          change: '+3',
          changeType: 'increase',
          icon: DocumentCheckIcon,
          gradient: 'from-amber-400/90 via-orange-400/80 to-yellow-400/90'
        },
        {
          name: '後継技能者数',
          value: '320',
          change: '+8',
          changeType: 'increase',
          icon: UserGroupIcon,
          gradient: 'from-emerald-400/90 via-emerald-500/90 to-teal-500/90'
        },
        {
          name: '派遣中後継技能者',
          value: '305',
          change: '-2',
          changeType: 'decrease',
          icon: UserGroupIcon,
          gradient: 'from-emerald-500/90 via-green-500/80 to-emerald-600/90'
        },
        {
          name: '企業数',
          value: '20',
          change: '0',
          changeType: 'neutral',
          icon: BuildingOfficeIcon,
          gradient: 'from-violet-400/90 via-purple-400/80 to-indigo-500/90'
        },
        {
          name: '承認待ち申請',
          value: '8',
          change: '+2',
          changeType: 'increase',
          icon: ClockIcon,
          gradient: 'from-orange-400/90 via-amber-400/80 to-rose-400/90'
        },
        {
          name: '今月給与支給額',
          value: '¥45,000,000',
          change: '+5.2%',
          changeType: 'increase',
          icon: CurrencyYenIcon,
          gradient: 'from-emerald-400/90 via-emerald-500/80 to-green-600/90'
        },
        {
          name: '今月利益',
          value: '¥8,500,000',
          change: '+3.8%',
          changeType: 'increase',
          icon: ArrowTrendingUpIcon,
          gradient: 'from-indigo-400/90 via-blue-500/80 to-purple-500/90'
        }
      ]);
      setAlerts([
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
      ]);
      setRecentActivities([
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
      ]);
      setTopFactories([
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
      ]);
      
      setLoading(false);
    };

    fetchData();
  }, []);

  return { stats, alerts, recentActivities, topFactories, loading };
};

export default useDashboardData;
