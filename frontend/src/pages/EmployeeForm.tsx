import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeftIcon, UserPlusIcon, PencilIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface EmployeeFormData {
  uns_id: string;
  factory_id: string;
  hakensaki_shain_id: string;
  full_name_kanji: string;
  full_name_kana: string;
  date_of_birth: string;
  gender: string;
  nationality: string;
  zairyu_card_number: string;
  zairyu_expire_date: string;
  address: string;
  phone: string;
  email: string;
  emergency_contact: string;
  emergency_phone: string;
  hire_date: string;
  jikyu: number;
  position: string;
  contract_type: string;
  apartment_id: string;
  apartment_start_date: string;
  apartment_rent: string;
}

const EmployeeForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = id && id !== 'new';

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState<EmployeeFormData>({
    uns_id: '',
    factory_id: '',
    hakensaki_shain_id: '',
    full_name_kanji: '',
    full_name_kana: '',
    date_of_birth: '',
    gender: '男',
    nationality: '',
    zairyu_card_number: '',
    zairyu_expire_date: '',
    address: '',
    phone: '',
    email: '',
    emergency_contact: '',
    emergency_phone: '',
    hire_date: new Date().toISOString().split('T')[0],
    jikyu: 1000,
    position: '',
    contract_type: '派遣',
    apartment_id: '',
    apartment_start_date: '',
    apartment_rent: '',
  });

  useEffect(() => {
    if (isEdit) {
      fetchEmployee();
    }
  }, [id]);

  const fetchEmployee = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/employees/${id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      const employee = response.data;
      setFormData({
        uns_id: employee.uns_id || '',
        factory_id: employee.factory_id || '',
        hakensaki_shain_id: employee.hakensaki_shain_id || '',
        full_name_kanji: employee.full_name_kanji || '',
        full_name_kana: employee.full_name_kana || '',
        date_of_birth: employee.date_of_birth || '',
        gender: employee.gender || '男',
        nationality: employee.nationality || '',
        zairyu_card_number: employee.zairyu_card_number || '',
        zairyu_expire_date: employee.zairyu_expire_date || '',
        address: employee.address || '',
        phone: employee.phone || '',
        email: employee.email || '',
        emergency_contact: employee.emergency_contact || '',
        emergency_phone: employee.emergency_phone || '',
        hire_date: employee.hire_date || '',
        jikyu: employee.jikyu || 1000,
        position: employee.position || '',
        contract_type: employee.contract_type || '派遣',
        apartment_id: employee.apartment_id ? employee.apartment_id.toString() : '',
        apartment_start_date: employee.apartment_start_date || '',
        apartment_rent: employee.apartment_rent ? employee.apartment_rent.toString() : '',
      });
    } catch (err: any) {
      toast.error('従業員情報の読み込みに失敗しました');
      console.error('Error fetching employee:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.full_name_kanji) {
      toast.error('氏名（漢字）を入力してください');
      return;
    }
    if (!formData.hire_date) {
      toast.error('入社日を入力してください');
      return;
    }
    if (!formData.jikyu || formData.jikyu < 0) {
      toast.error('時給を正しく入力してください');
      return;
    }
    if (!isEdit && !formData.uns_id) {
      toast.error('UNS-IDを入力してください');
      return;
    }
    if (!formData.factory_id) {
      toast.error('派遣先IDを入力してください');
      return;
    }

    try {
      setSubmitting(true);
      const token = localStorage.getItem('token');

      // Prepare data
      const submitData: any = {
        full_name_kanji: formData.full_name_kanji,
        full_name_kana: formData.full_name_kana || null,
        date_of_birth: formData.date_of_birth || null,
        gender: formData.gender || null,
        nationality: formData.nationality || null,
        zairyu_card_number: formData.zairyu_card_number || null,
        zairyu_expire_date: formData.zairyu_expire_date || null,
        address: formData.address || null,
        phone: formData.phone || null,
        email: formData.email || null,
        emergency_contact: formData.emergency_contact || null,
        emergency_phone: formData.emergency_phone || null,
        factory_id: formData.factory_id,
        hakensaki_shain_id: formData.hakensaki_shain_id || null,
        jikyu: parseInt(formData.jikyu.toString()),
        position: formData.position || null,
      };

      if (!isEdit) {
        // Create new employee
        submitData.uns_id = formData.uns_id;
        submitData.hire_date = formData.hire_date;
        submitData.contract_type = formData.contract_type;
        submitData.apartment_id = formData.apartment_id ? parseInt(formData.apartment_id) : null;
        submitData.apartment_start_date = formData.apartment_start_date || null;
        submitData.apartment_rent = formData.apartment_rent ? parseInt(formData.apartment_rent) : null;

        await axios.post('http://localhost:8000/api/employees/', submitData, {
          headers: { Authorization: `Bearer ${token}` },
        });

        toast.success('従業員を登録しました');
      } else {
        // Update existing employee
        await axios.put(`http://localhost:8000/api/employees/${id}`, submitData, {
          headers: { Authorization: `Bearer ${token}` },
        });

        toast.success('従業員情報を更新しました');
      }

      navigate('/employees');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '保存に失敗しました';
      toast.error(errorMessage);
      console.error('Error saving employee:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/employees')}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            戻る
          </button>
          <h1 className="text-2xl font-bold text-gray-900">
            {isEdit ? '従業員情報編集' : '従業員新規登録'}
          </h1>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Personal Information */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">個人情報</h2>
          </div>
          <div className="px-6 py-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {!isEdit && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    UNS-ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="uns_id"
                    value={formData.uns_id}
                    onChange={handleChange}
                    required
                    placeholder="UNS-2025-001"
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              )}

              <div className={!isEdit ? '' : 'md:col-span-2'}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  氏名（漢字） <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="full_name_kanji"
                  value={formData.full_name_kanji}
                  onChange={handleChange}
                  required
                  placeholder="山田 太郎"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  氏名（カナ）
                </label>
                <input
                  type="text"
                  name="full_name_kana"
                  value={formData.full_name_kana}
                  onChange={handleChange}
                  placeholder="ヤマダ タロウ"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  生年月日
                </label>
                <input
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  性別
                </label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="男">男</option>
                  <option value="女">女</option>
                  <option value="その他">その他</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  国籍
                </label>
                <input
                  type="text"
                  name="nationality"
                  value={formData.nationality}
                  onChange={handleChange}
                  placeholder="日本"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  在留カード番号
                </label>
                <input
                  type="text"
                  name="zairyu_card_number"
                  value={formData.zairyu_card_number}
                  onChange={handleChange}
                  placeholder="AB1234567"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  在留カード有効期限
                </label>
                <input
                  type="date"
                  name="zairyu_expire_date"
                  value={formData.zairyu_expire_date}
                  onChange={handleChange}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">連絡先情報</h2>
          </div>
          <div className="px-6 py-4 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                住所
              </label>
              <textarea
                name="address"
                value={formData.address}
                onChange={handleChange}
                rows={2}
                placeholder="愛知県名古屋市..."
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  電話番号
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="090-1234-5678"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  メールアドレス
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="example@email.com"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  緊急連絡先（氏名）
                </label>
                <input
                  type="text"
                  name="emergency_contact"
                  value={formData.emergency_contact}
                  onChange={handleChange}
                  placeholder="山田 花子"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  緊急連絡先（電話番号）
                </label>
                <input
                  type="tel"
                  name="emergency_phone"
                  value={formData.emergency_phone}
                  onChange={handleChange}
                  placeholder="090-8765-4321"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Employment Information */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">雇用情報</h2>
          </div>
          <div className="px-6 py-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {!isEdit && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    入社日 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    name="hire_date"
                    value={formData.hire_date}
                    onChange={handleChange}
                    required
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              )}

              {!isEdit && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    契約形態
                  </label>
                  <select
                    name="contract_type"
                    value={formData.contract_type}
                    onChange={handleChange}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="派遣">派遣社員</option>
                    <option value="請負">請負社員</option>
                    <option value="スタッフ">スタッフ</option>
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  派遣先ID <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="factory_id"
                  value={formData.factory_id}
                  onChange={handleChange}
                  required
                  placeholder="Factory-01"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  派遣先社員ID
                </label>
                <input
                  type="text"
                  name="hakensaki_shain_id"
                  value={formData.hakensaki_shain_id}
                  onChange={handleChange}
                  placeholder="派遣先での社員番号"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  時給 <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-500">
                    ¥
                  </span>
                  <input
                    type="number"
                    name="jikyu"
                    value={formData.jikyu}
                    onChange={handleChange}
                    required
                    min="0"
                    step="10"
                    className="block w-full pl-7 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  職種
                </label>
                <input
                  type="text"
                  name="position"
                  value={formData.position}
                  onChange={handleChange}
                  placeholder="製造作業員"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Apartment Information (only for new employees) */}
        {!isEdit && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">寮・住居情報（任意）</h2>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    寮ID
                  </label>
                  <input
                    type="text"
                    name="apartment_id"
                    value={formData.apartment_id}
                    onChange={handleChange}
                    placeholder="1"
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    入居日
                  </label>
                  <input
                    type="date"
                    name="apartment_start_date"
                    value={formData.apartment_start_date}
                    onChange={handleChange}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    家賃
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-500">
                      ¥
                    </span>
                    <input
                      type="number"
                      name="apartment_rent"
                      value={formData.apartment_rent}
                      onChange={handleChange}
                      min="0"
                      step="1000"
                      placeholder="30000"
                      className="block w-full pl-7 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/employees')}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            キャンセル
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {submitting ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                保存中...
              </>
            ) : (
              <>
                {isEdit ? (
                  <>
                    <PencilIcon className="h-5 w-5 mr-2" />
                    更新
                  </>
                ) : (
                  <>
                    <UserPlusIcon className="h-5 w-5 mr-2" />
                    登録
                  </>
                )}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EmployeeForm;
