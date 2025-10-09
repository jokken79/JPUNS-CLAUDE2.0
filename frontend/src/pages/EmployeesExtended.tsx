import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  MagnifyingGlassIcon,
  UserPlusIcon,
  PencilIcon,
  EyeIcon,
  PhotoIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';
import VisaAlert from '../components/VisaAlert';
import ColumnSelector from '../components/ColumnSelector';

interface Employee {
  id: number;
  hakenmoto_id: number;
  factory_id: string | null;
  factory_name: string | null;  // Nombre de la fábrica
  full_name_kanji: string;
  full_name_kana: string | null;
  gender: string | null;
  nationality: string | null;
  date_of_birth: string | null;
  jikyu: number;
  hourly_rate_charged: number | null;
  profit_difference: number | null;
  standard_compensation: number | null;
  health_insurance: number | null;
  nursing_insurance: number | null;
  pension_insurance: number | null;
  zairyu_expire_date: string | null;
  visa_type: string | null;
  postal_code: string | null;
  address: string | null;
  apartment_id: number | null;
  apartment_start_date: string | null;
  hire_date: string;
  termination_date: string | null;
  apartment_move_out_date: string | null;
  social_insurance_date: string | null;
  entry_request_date: string | null;
  notes: string | null;
  license_type: string | null;
  license_expire_date: string | null;
  commute_method: string | null;
  optional_insurance_expire: string | null;
  japanese_level: string | null;
  career_up_5years: boolean | null;
  is_active: boolean;
  photo_url: string | null;
  contract_type: string | null;
}

const EmployeesExtended: React.FC = () => {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterActive, setFilterActive] = useState<boolean | null>(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 500; // Mostrar hasta 500 empleados por página

  useEffect(() => {
    fetchEmployees();
  }, [currentPage, searchTerm, filterActive]);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');

      const params: any = {
        page: currentPage,
        page_size: pageSize,
      };

      if (searchTerm) params.search = searchTerm;
      if (filterActive !== null) params.is_active = filterActive;

      const response = await axios.get(
        'http://localhost:8000/api/employees/',
        {
          headers: { Authorization: `Bearer ${token}` },
          params,
        }
      );

      setEmployees(response.data.items);
      setTotal(response.data.total);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar empleados');
      console.error('Error fetching employees:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).replace(/\//g, '/');
  };

  const formatCurrency = (amount: number | null) => {
    if (!amount) return '-';
    return `¥${amount.toLocaleString()}`;
  };

  const calculateAge = (birthDate: string | null) => {
    if (!birthDate) return '-';
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const getVisaAlert = (expireDate: string | null) => {
    if (!expireDate) return '';
    const expire = new Date(expireDate);
    const today = new Date();
    const diffInDays = Math.ceil((expire.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    if (diffInDays < 0) return '期限切れ';
    if (diffInDays <= 30) return '要更新';
    if (diffInDays <= 90) return '注意';
    return '';
  };

  const getVisaAlertColor = (alert: string) => {
    if (alert === '期限切れ') return 'bg-red-100 text-red-800';
    if (alert === '要更新') return 'bg-orange-100 text-orange-800';
    if (alert === '注意') return 'bg-yellow-100 text-yellow-800';
    return '';
  };

  if (loading && employees.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">従業員管理（詳細）</h1>
          <p className="mt-1 text-sm text-gray-500">
            全{total}名の従業員を管理
          </p>
        </div>
        <button
          onClick={() => navigate('/employees/new')}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
        >
          <UserPlusIcon className="h-5 w-5 mr-2" />
          新規登録
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              検索
            </label>
            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="氏名または社員番号で検索..."
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              在籍状況
            </label>
            <select
              value={filterActive === null ? '' : filterActive.toString()}
              onChange={(e) => {
                const value = e.target.value;
                setFilterActive(value === '' ? null : value === 'true');
                setCurrentPage(1);
              }}
              className="block w-full py-2 px-3 border border-gray-300 rounded-md"
            >
              <option value="">全て</option>
              <option value="true">在籍中</option>
              <option value="false">退社済</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Employees Table */}
      <div className="bg-white shadow overflow-hidden rounded-lg">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-xs">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">現在</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">社員№</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">派遣先</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">氏名</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">カナ</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">性別</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">国籍</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">生年月日</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">年齢</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">時給</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">請求単価</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">差額利益</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">標準報酬</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">健康保険</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">介護保険</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">厚生年金</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">ビザ期限</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">ｱﾗｰﾄ</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">ビザ種類</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">〒</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">住所</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">ｱﾊﾟｰﾄ</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">入居</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">入社日</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">退社日</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">退去</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">社保加入</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">入社依頼</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">備考</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">免許種類</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">免許期限</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">通勤方法</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">任意保険期限</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">日本語検定</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">キャリアアップ5年目</th>
                <th className="px-2 py-3 text-left font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {employees.length === 0 ? (
                <tr>
                  <td colSpan={36} className="px-6 py-12 text-center text-sm text-gray-500">
                    従業員が見つかりませんでした
                  </td>
                </tr>
              ) : (
                employees.map((employee) => {
                  const visaAlert = getVisaAlert(employee.zairyu_expire_date);
                  return (
                    <tr key={employee.id} className="hover:bg-gray-50">
                      <td className="px-2 py-2 whitespace-nowrap">
                        {employee.photo_url && (
                          <PhotoIcon className="h-5 w-5 text-blue-500 cursor-pointer" title="写真あり" />
                        )}
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap font-medium text-gray-900">
                        {employee.hakenmoto_id}
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.factory_name || employee.factory_id || '-'}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.full_name_kanji}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.full_name_kana || '-'}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.gender || '-'}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.nationality || '-'}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatDate(employee.date_of_birth)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{calculateAge(employee.date_of_birth)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatCurrency(employee.jikyu)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatCurrency(employee.hourly_rate_charged)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatCurrency(employee.profit_difference)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatCurrency(employee.standard_compensation)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatCurrency(employee.health_insurance)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatCurrency(employee.nursing_insurance)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatCurrency(employee.pension_insurance)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatDate(employee.zairyu_expire_date)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">
                        {visaAlert && (
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getVisaAlertColor(visaAlert)}`}>
                            {visaAlert}
                          </span>
                        )}
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.visa_type || '-'}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.postal_code || '-'}</td>
                      <td className="px-2 py-2 max-w-xs truncate" title={employee.address || ''}>
                        {employee.address || '-'}
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.apartment_id || '-'}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatDate(employee.apartment_start_date)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatDate(employee.hire_date)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatDate(employee.termination_date)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatDate(employee.apartment_move_out_date)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatDate(employee.social_insurance_date)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatDate(employee.entry_request_date)}</td>
                      <td className="px-2 py-2 max-w-xs truncate" title={employee.notes || ''}>
                        {employee.notes || '-'}
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.license_type || '-'}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatDate(employee.license_expire_date)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.commute_method || '-'}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{formatDate(employee.optional_insurance_expire)}</td>
                      <td className="px-2 py-2 whitespace-nowrap">{employee.japanese_level || '-'}</td>
                      <td className="px-2 py-2 whitespace-nowrap text-center">
                        {employee.career_up_5years ? '○' : '-'}
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap">
                        <button
                          onClick={() => navigate(`/employees/${employee.id}`)}
                          className="text-blue-600 hover:text-blue-900 mr-2"
                          title="詳細"
                        >
                          <EyeIcon className="h-4 w-4 inline" />
                        </button>
                        <button
                          onClick={() => navigate(`/employees/${employee.id}/edit`)}
                          className="text-gray-600 hover:text-gray-900"
                          title="編集"
                        >
                          <PencilIcon className="h-4 w-4 inline" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {total > pageSize && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
            <div>
              <p className="text-sm text-gray-700">
                <span className="font-medium">{total}</span> 件中{' '}
                <span className="font-medium">{(currentPage - 1) * pageSize + 1}</span> -{' '}
                <span className="font-medium">
                  {Math.min(currentPage * pageSize, total)}
                </span>{' '}
                件を表示
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400"
                >
                  前へ
                </button>
                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage * pageSize >= total}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400"
                >
                  次へ
                </button>
              </nav>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmployeesExtended;
