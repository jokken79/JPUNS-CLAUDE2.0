import React, { useState, useEffect } from 'react';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  UserPlusIcon,
  PencilIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface Employee {
  id: number;
  hakenmoto_id: number;
  uns_id: string;
  full_name_kanji: string;
  full_name_kana: string | null;
  factory_id: string;
  factory_name: string | null;  // Nombre de la fábrica
  hire_date: string;
  jikyu: number;
  contract_type: string | null;
  is_active: boolean;
  nationality: string | null;
  phone: string | null;
  email: string | null;
  zairyu_expire_date: string | null;
  yukyu_remaining: number;
  termination_date: string | null;
}

interface PaginatedResponse {
  items: Employee[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

type ColumnKey =
  | 'employeeNumber'
  | 'fullName'
  | 'kanaName'
  | 'contractType'
  | 'factory'
  | 'hourlyWage'
  | 'hireDate'
  | 'status'
  | 'actions';

interface ColumnDefinition {
  key: ColumnKey;
  label: string;
  headerClassName: string;
  cellClassName: string;
  render: (employee: Employee) => React.ReactNode;
}

const Employees: React.FC = () => {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterActive, setFilterActive] = useState<boolean | null>(null);
  const [filterFactory, setFilterFactory] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [visibleColumns, setVisibleColumns] = useState<Record<ColumnKey, boolean>>({
    employeeNumber: true,
    fullName: true,
    kanaName: true,
    contractType: true,
    factory: true,
    hourlyWage: true,
    hireDate: true,
    status: true,
    actions: true,
  });
  const pageSize = 500; // Mostrar hasta 500 empleados por página

  useEffect(() => {
    fetchEmployees();
  }, [currentPage, searchTerm, filterActive, filterFactory]);

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
      if (filterFactory) params.factory_id = filterFactory;

      const response = await axios.get<PaginatedResponse>(
        'http://localhost:8000/api/employees',
        {
          headers: { Authorization: `Bearer ${token}` },
          params,
        }
      );

      setEmployees(response.data.items);
      setTotal(response.data.total);
      setTotalPages(response.data.total_pages);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar empleados');
      console.error('Error fetching employees:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchEmployees();
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
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          在籍中
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
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
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${type.color}`}>
        {type.label}
      </span>
    );
  };

  const columnDefinitions: ColumnDefinition[] = [
    {
      key: 'employeeNumber',
      label: '社員№',
      headerClassName:
        'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      cellClassName: 'px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900',
      render: (employee) => employee.hakenmoto_id,
    },
    {
      key: 'fullName',
      label: '氏名',
      headerClassName:
        'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      cellClassName: 'px-6 py-4 whitespace-nowrap text-sm text-gray-900',
      render: (employee) => employee.full_name_kanji,
    },
    {
      key: 'kanaName',
      label: 'カナ',
      headerClassName:
        'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      cellClassName: 'px-6 py-4 whitespace-nowrap text-sm text-gray-500',
      render: (employee) => employee.full_name_kana || '-',
    },
    {
      key: 'contractType',
      label: '契約形態',
      headerClassName:
        'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      cellClassName: 'px-6 py-4 whitespace-nowrap text-sm',
      render: (employee) => getContractTypeBadge(employee.contract_type),
    },
    {
      key: 'factory',
      label: '派遣先',
      headerClassName:
        'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      cellClassName: 'px-6 py-4 whitespace-nowrap text-sm text-gray-900',
      render: (employee) => employee.factory_name || employee.factory_id || '-',
    },
    {
      key: 'hourlyWage',
      label: '時給',
      headerClassName:
        'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      cellClassName: 'px-6 py-4 whitespace-nowrap text-sm text-gray-900',
      render: (employee) => formatCurrency(employee.jikyu),
    },
    {
      key: 'hireDate',
      label: '入社日',
      headerClassName:
        'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      cellClassName: 'px-6 py-4 whitespace-nowrap text-sm text-gray-500',
      render: (employee) => formatDate(employee.hire_date),
    },
    {
      key: 'status',
      label: '状態',
      headerClassName:
        'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      cellClassName: 'px-6 py-4 whitespace-nowrap',
      render: (employee) => getStatusBadge(employee.is_active),
    },
    {
      key: 'actions',
      label: '操作',
      headerClassName:
        'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
      cellClassName: 'px-6 py-4 whitespace-nowrap text-sm font-medium',
      render: (employee) => (
        <>
          <button
            onClick={() => navigate(`/employees/${employee.id}`)}
            className="text-blue-600 hover:text-blue-900 mr-3"
            title="詳細を見る"
          >
            <EyeIcon className="h-5 w-5 inline" />
          </button>
          <button
            onClick={() => navigate(`/employees/${employee.id}/edit`)}
            className="text-gray-600 hover:text-gray-900"
            title="編集"
          >
            <PencilIcon className="h-5 w-5 inline" />
          </button>
        </>
      ),
    },
  ];

  const handleColumnToggle = (key: ColumnKey) => {
    setVisibleColumns((prev) => {
      const visibleCount = Object.values(prev).filter(Boolean).length;

      if (visibleCount <= 1 && prev[key]) {
        return prev;
      }

      return {
        ...prev,
        [key]: !prev[key],
      };
    });
  };

  const visibleColumnDefinitions = columnDefinitions.filter(
    (column) => visibleColumns[column.key]
  );

  if (loading && employees.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const activeCount = employees.filter(e => e.is_active).length;
  const inactiveCount = employees.filter(e => !e.is_active).length;

  return (
    <div className="space-y-4">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold opacity-90">総従業員数</h3>
            <svg className="w-8 h-8 opacity-80" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
            </svg>
          </div>
          <p className="text-4xl font-black">{total}</p>
          <p className="text-xs opacity-75 mt-1">登録済みデータベース</p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold opacity-90">在籍中</h3>
            <svg className="w-8 h-8 opacity-80" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-4xl font-black">{activeCount}</p>
          <p className="text-xs opacity-75 mt-1">アクティブ従業員</p>
        </div>

        <div className="bg-gradient-to-br from-gray-500 to-slate-600 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold opacity-90">退社済</h3>
            <svg className="w-8 h-8 opacity-80" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-4xl font-black">{inactiveCount}</p>
          <p className="text-xs opacity-75 mt-1">非アクティブ</p>
        </div>
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-gray-900">従業員管理</h1>
          <p className="mt-1 text-sm text-gray-600">
            全{total}名の従業員を管理
          </p>
        </div>
        <button
          onClick={() => navigate('/employees/new')}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-xl font-semibold shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 transition-all duration-300 hover:scale-105"
        >
          <UserPlusIcon className="h-5 w-5" />
          新規登録
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white/80 backdrop-blur rounded-2xl border border-gray-200 p-4 shadow-sm">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                検索
              </label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="氏名または社員番号で検索..."
                  className="block w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                在籍状況
              </label>
              <div className="relative">
                <FunnelIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
                <select
                  value={filterActive === null ? '' : filterActive.toString()}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFilterActive(value === '' ? null : value === 'true');
                    setCurrentPage(1);
                  }}
                  className="block w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition appearance-none"
                >
                  <option value="">全て</option>
                  <option value="true">在籍中</option>
                  <option value="false">退社済</option>
                </select>
              </div>
            </div>

            {/* Factory Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                派遣先
              </label>
              <input
                type="text"
                value={filterFactory}
                onChange={(e) => {
                  setFilterFactory(e.target.value);
                  setCurrentPage(1);
                }}
                placeholder="Factory-XX"
                className="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>

          <div className="pt-4 border-t border-gray-200">
            <span className="block text-sm font-medium text-gray-700 mb-2">
              表示する列
            </span>
            <div className="flex flex-wrap gap-4">
              {columnDefinitions.map((column) => (
                <label key={column.key} className="inline-flex items-center text-sm text-gray-700">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    checked={visibleColumns[column.key]}
                    onChange={() => handleColumnToggle(column.key)}
                  />
                  <span className="ml-2">{column.label}</span>
                </label>
              ))}
            </div>
            <p className="mt-2 text-xs text-gray-500">※最低1列は表示する必要があります。</p>
          </div>
        </form>
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
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {visibleColumnDefinitions.map((column) => (
                  <th key={column.key} className={column.headerClassName}>
                    {column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {employees.length === 0 ? (
                <tr>
                  <td
                    colSpan={visibleColumnDefinitions.length}
                    className="px-6 py-12 text-center text-sm text-gray-500"
                  >
                    従業員が見つかりませんでした
                  </td>
                </tr>
              ) : (
                employees.map((employee) => (
                  <tr key={employee.id} className="hover:bg-gray-50">
                    {visibleColumnDefinitions.map((column) => (
                      <td key={column.key} className={column.cellClassName}>
                        {column.render(employee)}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400"
              >
                前へ
              </button>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400"
              >
                次へ
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
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
                  {[...Array(Math.min(5, totalPages))].map((_, idx) => {
                    const page = idx + 1;
                    return (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          currentPage === page
                            ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    );
                  })}
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400"
                  >
                    次へ
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Employees;
