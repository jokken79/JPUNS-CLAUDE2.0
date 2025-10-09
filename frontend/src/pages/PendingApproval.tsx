import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import {
  UserPlusIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';

type CandidateStatus = 'pending' | 'approved' | 'rejected' | 'hired';

interface Candidate {
  id: number;
  rirekisho_id: string;
  full_name_kanji?: string;
  full_name_kana?: string;
  nationality?: string;
  date_of_birth?: string;
  phone?: string;
  mobile?: string;
  status?: CandidateStatus;
  reception_date?: string;
  photo_url?: string;
}

const statusConfig = {
  pending: {
    label: '承認待ち',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    textColor: 'text-yellow-700',
    icon: ClockIcon,
    iconColor: 'text-yellow-500'
  },
  approved: {
    label: '承認済み',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    textColor: 'text-green-700',
    icon: CheckCircleIcon,
    iconColor: 'text-green-500'
  },
  rejected: {
    label: '却下',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    textColor: 'text-red-700',
    icon: XCircleIcon,
    iconColor: 'text-red-500'
  },
  hired: {
    label: '採用済み',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-700',
    icon: CheckCircleIcon,
    iconColor: 'text-blue-500'
  }
};

const PendingApproval: React.FC = () => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<CandidateStatus | 'all'>('all');

  useEffect(() => {
    fetchCandidates();
  }, [statusFilter]);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (statusFilter !== 'all') {
        params.append('status_filter', statusFilter);
      }

      const response = await fetch(`/api/candidates/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch candidates');

      const data = await response.json();
      setCandidates(data.items || []);
    } catch (error) {
      toast.error('候補者の取得に失敗しました');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/candidates/${id}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error('Failed to approve');

      toast.success('候補者を承認しました。従業員として登録されました。');
      fetchCandidates();
    } catch (error) {
      toast.error('承認に失敗しました');
    }
  };

  const handleReject = async (id: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/candidates/${id}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason: '不適合' })
      });

      if (!response.ok) throw new Error('Failed to reject');

      toast.success('候補者を却下しました。候補者データベースに保存されました。');
      fetchCandidates();
    } catch (error) {
      toast.error('却下に失敗しました');
    }
  };

  const filteredCandidates = candidates.filter(candidate => {
    const searchLower = searchTerm.toLowerCase();
    return (
      candidate.full_name_kanji?.toLowerCase().includes(searchLower) ||
      candidate.full_name_kana?.toLowerCase().includes(searchLower) ||
      candidate.rirekisho_id?.toLowerCase().includes(searchLower) ||
      candidate.nationality?.toLowerCase().includes(searchLower)
    );
  });

  // Contar candidatos por estado
  const pendingCount = candidates.filter(c => c.status === 'pending').length;
  const approvedCount = candidates.filter(c => c.status === 'approved').length;
  const rejectedCount = candidates.filter(c => c.status === 'rejected').length;

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-yellow-500 to-amber-600 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold opacity-90">承認待ち</h3>
            <ClockIcon className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-4xl font-black">{pendingCount}</p>
          <p className="text-xs opacity-75 mt-1">審査が必要です</p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold opacity-90">承認済み</h3>
            <CheckCircleIcon className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-4xl font-black">{approvedCount}</p>
          <p className="text-xs opacity-75 mt-1">従業員として登録済み</p>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-rose-600 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold opacity-90">却下済み</h3>
            <XCircleIcon className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-4xl font-black">{rejectedCount}</p>
          <p className="text-xs opacity-75 mt-1">候補者DBに保存</p>
        </div>
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-gray-900">承認待ち</h1>
          <p className="mt-1 text-sm text-gray-600">候補者の審査・承認を行います</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white/80 backdrop-blur rounded-2xl border border-gray-200 p-4 shadow-sm">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="名前・ID・国籍で検索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="sm:w-48">
            <div className="relative">
              <FunnelIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as CandidateStatus | 'all')}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition appearance-none"
              >
                <option value="all">すべて</option>
                <option value="pending">承認待ち</option>
                <option value="approved">承認済み</option>
                <option value="rejected">却下</option>
                <option value="hired">採用済み</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Candidates Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white/80 rounded-2xl border border-gray-200 p-6 animate-pulse">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-gray-200 rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4" />
                  <div className="h-3 bg-gray-200 rounded w-1/2" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : filteredCandidates.length === 0 ? (
        <div className="bg-white/80 backdrop-blur rounded-2xl border border-gray-200 p-12 text-center">
          <UserPlusIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">候補者がいません</h3>
          <p className="text-gray-600">検索条件を変更するか、新しい候補者を登録してください</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCandidates.map((candidate) => {
            const status = candidate.status || 'pending';
            const config = statusConfig[status];
            const StatusIcon = config.icon;

            return (
              <div
                key={candidate.id}
                className="group relative bg-white/90 backdrop-blur rounded-2xl border border-gray-200 hover:border-indigo-300 p-6 shadow-sm hover:shadow-xl transition-all duration-300 hover:scale-[1.02]"
              >
                {/* Status Badge */}
                <div className={`absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${config.bgColor} ${config.borderColor}`}>
                  <StatusIcon className={`h-4 w-4 ${config.iconColor}`} />
                  <span className={`text-xs font-semibold ${config.textColor}`}>
                    {config.label}
                  </span>
                </div>

                {/* Candidate Info */}
                <div className="flex items-start gap-4 mb-5 mt-2">
                  <div className="flex-shrink-0">
                    {candidate.photo_url ? (
                      <img
                        src={candidate.photo_url}
                        alt={candidate.full_name_kanji || '候補者'}
                        className="w-16 h-16 rounded-full object-cover border-2 border-gray-200"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-xl">
                        {candidate.full_name_kanji?.charAt(0) || '?'}
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-gray-900 text-lg truncate">
                      {candidate.full_name_kanji || '未設定'}
                    </h3>
                    <p className="text-sm text-gray-600 truncate">{candidate.full_name_kana}</p>
                    <p className="text-xs text-gray-500 mt-1">ID: {candidate.rirekisho_id}</p>
                  </div>
                </div>

                {/* Details */}
                <div className="space-y-2 mb-5 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">国籍:</span>
                    <span className="font-semibold text-gray-900">{candidate.nationality || '未設定'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">受付日:</span>
                    <span className="font-semibold text-gray-900">
                      {candidate.reception_date ? new Date(candidate.reception_date).toLocaleDateString('ja-JP') : '未設定'}
                    </span>
                  </div>
                  {candidate.mobile && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">電話:</span>
                      <span className="font-semibold text-gray-900">{candidate.mobile}</span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-4 border-t border-gray-200">
                  {status === 'pending' && (
                    <>
                      <button
                        onClick={() => handleApprove(candidate.id)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl font-semibold text-sm hover:shadow-lg hover:shadow-green-500/30 transition-all duration-300"
                        title="承認すると従業員DBに登録されます"
                      >
                        <CheckCircleIcon className="h-4 w-4" />
                        承認
                      </button>
                      <button
                        onClick={() => handleReject(candidate.id)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-red-500 to-rose-500 text-white rounded-xl font-semibold text-sm hover:shadow-lg hover:shadow-red-500/30 transition-all duration-300"
                        title="却下しても候補者DBに保存されます"
                      >
                        <XCircleIcon className="h-4 w-4" />
                        却下
                      </button>
                    </>
                  )}
                  <Link
                    to={`/candidates/${candidate.id}`}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-xl font-semibold text-sm hover:bg-gray-200 transition-all duration-300"
                  >
                    詳細
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default PendingApproval;
