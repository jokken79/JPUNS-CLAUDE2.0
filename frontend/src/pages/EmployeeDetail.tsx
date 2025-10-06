import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  ArrowLeftIcon,
  PencilIcon,
  DocumentTextIcon,
  CalendarIcon,
  BanknotesIcon,
  HomeIcon,
  PhoneIcon,
  EnvelopeIcon,
  IdentificationIcon,
  UserCircleIcon,
  BuildingOfficeIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

interface Employee {
  id: number;
  hakenmoto_id: number;
  uns_id: string;
  factory_id: string;
  hakensaki_shain_id: string | null;
  full_name_kanji: string;
  full_name_kana: string | null;
  date_of_birth: string | null;
  gender: string | null;
  nationality: string | null;
  zairyu_card_number: string | null;
  zairyu_expire_date: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  emergency_contact: string | null;
  emergency_phone: string | null;
  hire_date: string;
  jikyu: number;
  position: string | null;
  contract_type: string | null;
  apartment_id: number | null;
  apartment_start_date: string | null;
  apartment_rent: number | null;
  yukyu_total: number;
  yukyu_used: number;
  yukyu_remaining: number;
  is_active: boolean;
  termination_date: string | null;
  termination_reason: string | null;
  created_at: string;
  updated_at: string | null;
}

const EmployeeDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEmployee();
  }, [id]);

  const fetchEmployee = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get<Employee>(
        `http://localhost:8000/api/employees/${id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setEmployee(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar el empleado');
      console.error('Error fetching employee:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('ja-JP');
  };

  const formatCurrency = (amount: number) => {
    return `¥${amount.toLocaleString()}`;
  };

  const getStatusBadge = (isActive: boolean) => {
    if (isActive) {
      return (
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
          在籍中
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
          退社済
        </span>
      );
    }
  };

  const getContractTypeBadge = (contractType: string | null) => {
    const types: { [key: string]: { label: string; color: string } } = {
      '派遣': { label: '派遣社員', color: 'bg-blue-100 text-blue-800' },
      '請負': { label: '請負社員', color: 'bg-purple-100 text-purple-800' },
      'スタッフ': { label: 'スタッフ', color: 'bg-yellow-100 text-yellow-800' },
    };

    const type = contractType ? types[contractType] : null;
    if (!type) return '-';

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${type.color}`}>
        {type.label}
      </span>
    );
  };

  const isVisaExpiringSoon = (expireDate: string | null) => {
    if (!expireDate) return false;
    const expire = new Date(expireDate);
    const today = new Date();
    const diffInDays = Math.ceil((expire.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diffInDays <= 90 && diffInDays >= 0;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !employee) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-sm text-red-800">{error || '従業員が見つかりませんでした'}</p>
        </div>
        <button
          onClick={() => navigate('/employees')}
          className="mt-4 inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-2" />
          戻る
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="flex items-start space-x-4">
          <button
            onClick={() => navigate('/employees')}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            戻る
          </button>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-gray-900">
                {employee.full_name_kanji}
              </h1>
              {getStatusBadge(employee.is_active)}
              {getContractTypeBadge(employee.contract_type)}
            </div>
            <p className="mt-1 text-sm text-gray-500">
              社員№ {employee.hakenmoto_id} | UNS-ID: {employee.uns_id}
            </p>
          </div>
        </div>
        <button
          onClick={() => navigate(`/employees/${employee.id}/edit`)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
        >
          <PencilIcon className="h-5 w-5 mr-2" />
          編集
        </button>
      </div>

      {/* Visa Expiring Soon Alert */}
      {employee.is_active && isVisaExpiringSoon(employee.zairyu_expire_date) && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                <strong>警告:</strong> 在留カードの有効期限が近づいています（期限: {formatDate(employee.zairyu_expire_date)}）
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Personal Information */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900 flex items-center">
                <UserCircleIcon className="h-6 w-6 mr-2 text-gray-400" />
                個人情報
              </h2>
            </div>
            <div className="px-6 py-4">
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">氏名（漢字）</dt>
                  <dd className="mt-1 text-sm text-gray-900">{employee.full_name_kanji}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">氏名（カナ）</dt>
                  <dd className="mt-1 text-sm text-gray-900">{employee.full_name_kana || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">生年月日</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatDate(employee.date_of_birth)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">性別</dt>
                  <dd className="mt-1 text-sm text-gray-900">{employee.gender || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">国籍</dt>
                  <dd className="mt-1 text-sm text-gray-900">{employee.nationality || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">在留カード番号</dt>
                  <dd className="mt-1 text-sm text-gray-900">{employee.zairyu_card_number || '-'}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">在留カード有効期限</dt>
                  <dd className={`mt-1 text-sm ${isVisaExpiringSoon(employee.zairyu_expire_date) ? 'text-yellow-600 font-semibold' : 'text-gray-900'}`}>
                    {formatDate(employee.zairyu_expire_date)}
                    {isVisaExpiringSoon(employee.zairyu_expire_date) && ' ⚠️'}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          {/* Contact Information */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900 flex items-center">
                <PhoneIcon className="h-6 w-6 mr-2 text-gray-400" />
                連絡先情報
              </h2>
            </div>
            <div className="px-6 py-4">
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500 flex items-center">
                    <HomeIcon className="h-4 w-4 mr-1" />
                    住所
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">{employee.address || '-'}</dd>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500 flex items-center">
                      <PhoneIcon className="h-4 w-4 mr-1" />
                      電話番号
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900">{employee.phone || '-'}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 flex items-center">
                      <EnvelopeIcon className="h-4 w-4 mr-1" />
                      メールアドレス
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900">{employee.email || '-'}</dd>
                  </div>
                </div>
                <div className="pt-4 border-t border-gray-200">
                  <h3 className="text-sm font-medium text-gray-700 mb-3">緊急連絡先</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">名前</dt>
                      <dd className="mt-1 text-sm text-gray-900">{employee.emergency_contact || '-'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">電話番号</dt>
                      <dd className="mt-1 text-sm text-gray-900">{employee.emergency_phone || '-'}</dd>
                    </div>
                  </div>
                </div>
              </dl>
            </div>
          </div>

          {/* Employment Information */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900 flex items-center">
                <BuildingOfficeIcon className="h-6 w-6 mr-2 text-gray-400" />
                雇用情報
              </h2>
            </div>
            <div className="px-6 py-4">
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">入社日</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatDate(employee.hire_date)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">契約形態</dt>
                  <dd className="mt-1 text-sm">{getContractTypeBadge(employee.contract_type)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">時給</dt>
                  <dd className="mt-1 text-lg font-semibold text-gray-900">{formatCurrency(employee.jikyu)}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">職種</dt>
                  <dd className="mt-1 text-sm text-gray-900">{employee.position || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">派遣先ID</dt>
                  <dd className="mt-1 text-sm text-gray-900">{employee.factory_id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">派遣先社員ID</dt>
                  <dd className="mt-1 text-sm text-gray-900">{employee.hakensaki_shain_id || '-'}</dd>
                </div>
                {!employee.is_active && (
                  <>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">退社日</dt>
                      <dd className="mt-1 text-sm text-gray-900">{formatDate(employee.termination_date)}</dd>
                    </div>
                    <div className="sm:col-span-2">
                      <dt className="text-sm font-medium text-gray-500">退社理由</dt>
                      <dd className="mt-1 text-sm text-gray-900">{employee.termination_reason || '-'}</dd>
                    </div>
                  </>
                )}
              </dl>
            </div>
          </div>

          {/* Apartment Information */}
          {employee.apartment_id && (
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900 flex items-center">
                  <HomeIcon className="h-6 w-6 mr-2 text-gray-400" />
                  寮・住居情報
                </h2>
              </div>
              <div className="px-6 py-4">
                <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">寮ID</dt>
                    <dd className="mt-1 text-sm text-gray-900">{employee.apartment_id}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">入居日</dt>
                    <dd className="mt-1 text-sm text-gray-900">{formatDate(employee.apartment_start_date)}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">家賃</dt>
                    <dd className="mt-1 text-sm text-gray-900">{employee.apartment_rent ? formatCurrency(employee.apartment_rent) : '-'}</dd>
                  </div>
                </dl>
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Quick Stats */}
        <div className="space-y-6">
          {/* Yukyu Card */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900 flex items-center">
                <CalendarIcon className="h-6 w-6 mr-2 text-gray-400" />
                有給休暇
              </h2>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">付与日数</dt>
                <dd className="mt-1 text-2xl font-bold text-gray-900">{employee.yukyu_total}日</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">使用日数</dt>
                <dd className="mt-1 text-2xl font-bold text-gray-900">{employee.yukyu_used}日</dd>
              </div>
              <div className="pt-4 border-t border-gray-200">
                <dt className="text-sm font-medium text-gray-500">残日数</dt>
                <dd className="mt-1 text-3xl font-bold text-blue-600">{employee.yukyu_remaining}日</dd>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">クイックアクション</h2>
            </div>
            <div className="px-6 py-4 space-y-2">
              <button className="w-full inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <ClockIcon className="h-5 w-5 mr-2 text-gray-400" />
                タイムカードを見る
              </button>
              <button className="w-full inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <BanknotesIcon className="h-5 w-5 mr-2 text-gray-400" />
                給与明細を見る
              </button>
              <button className="w-full inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <DocumentTextIcon className="h-5 w-5 mr-2 text-gray-400" />
                書類を見る
              </button>
            </div>
          </div>

          {/* System Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">システム情報</h3>
            <dl className="space-y-2 text-xs">
              <div>
                <dt className="text-gray-500">登録日時</dt>
                <dd className="text-gray-900">{new Date(employee.created_at).toLocaleString('ja-JP')}</dd>
              </div>
              {employee.updated_at && (
                <div>
                  <dt className="text-gray-500">更新日時</dt>
                  <dd className="text-gray-900">{new Date(employee.updated_at).toLocaleString('ja-JP')}</dd>
                </div>
              )}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeDetail;
