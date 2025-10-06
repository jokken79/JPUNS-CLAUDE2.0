import React, { useState } from 'react';
import {
  ArrowUpTrayIcon,
  DocumentArrowDownIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import axios from 'axios';

interface ImportResult {
  success: boolean;
  created: number;
  updated: number;
  errors: string[];
  total_processed: number;
}

const ImportData: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Por favor selecciona un archivo Excel');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);
      const token = localStorage.getItem('token');

      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post<ImportResult>(
        'http://localhost:8000/api/employees/import-excel',
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              console.log(`Upload Progress: ${percentCompleted}%`);
            }
          },
          timeout: 300000, // 5 minutes timeout for large files
        }
      );

      setResult(response.data);
      setSelectedFile(null);
      // Reset file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al importar archivo');
      console.error('Error importing file:', err);
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = () => {
    // Create template data with ALL columns from your Excel (including hidden ones)
    const template = [
      {
        '現在': '例: 在籍中',
        '社員№': '例: 100001',
        '派遣先ID': '例: PMI-001 (ID que la fábrica da al empleado)',
        '派遣先': '例: ピーエムアイ有限会社 - 本社工場',
        '配属先': '例: 製造部',
        '配属ライン': '例: ライン1',
        '仕事内容': '例: 組立作業',
        '氏名': '例: 山田太郎',
        'カナ': '例: ヤマダタロウ',
        '性別': '例: 男',
        '国籍': '例: ベトナム',
        '生年月日': '例: 1990/01/01',
        '年齢': '例: 34',
        '時給': '例: 1300',
        '時給改定': '例: 2024/04/01',
        '請求単価': '例: 1500',
        '請求改定': '例: 2024/04/01',
        '差額利益': '例: 200',
        '標準報酬': '例: 250000',
        '健康保険': '例: 12000',
        '介護保険': '例: 2500',
        '厚生年金': '例: 22000',
        'ビザ期限': '例: 2025/12/31',
        'ｱﾗｰﾄ(ﾋﾞｻﾞ更新)': '例: 要更新',
        'ビザ種類': '例: 技能実習',
        '〒': '例: 460-0001',
        '住所': '例: 愛知県名古屋市中区',
        'ｱﾊﾟｰﾄ': '例: 1',
        '入居': '例: 2024/01/01',
        '入社日': '例: 2024/01/15',
        '退社日': '例: (空白)',
        '退去': '例: (空白)',
        '社保加入': '例: 2024/02/01',
        '入社依頼': '例: 2023/12/01',
        '備考': '例: 特になし',
        '現入社': '例: (空白)',
        '免許種類': '例: 普通自動車',
        '免許期限': '例: 2028/12/31',
        '通勤方法': '例: 自転車',
        '任意保険期限': '例: 2025/12/31',
        '日本語検定': '例: N3',
        'キャリアアップ5年目': '例: ○',
      },
    ];

    // Convert to CSV with UTF-8 BOM for Excel compatibility
    const headers = Object.keys(template[0]);
    const csvContent =
      '\uFEFF' + // UTF-8 BOM for Excel
      headers.join(',') +
      '\n' +
      template.map((row) => Object.values(row).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'plantilla_empleados.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">データインポート</h1>
        <p className="mt-1 text-sm text-gray-500">
          Excelファイルから従業員データを一括インポート
        </p>
      </div>

      {/* Download Template */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <DocumentArrowDownIcon className="h-6 w-6 text-blue-600 mt-0.5" />
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-blue-900">
              テンプレートをダウンロード
            </h3>
            <p className="mt-1 text-sm text-blue-700">
              Excelファイルのフォーマットに従ってデータを準備してください
            </p>
            <button
              onClick={downloadTemplate}
              className="mt-3 inline-flex items-center px-4 py-2 border border-blue-300 rounded-md shadow-sm text-sm font-medium text-blue-700 bg-white hover:bg-blue-50"
            >
              <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
              テンプレートダウンロード
            </button>
          </div>
        </div>
      </div>

      {/* Upload Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          ファイルをアップロード
        </h2>

        <div className="space-y-4">
          {/* File Input */}
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <ArrowUpTrayIcon className="w-12 h-12 mb-3 text-gray-400" />
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">クリックしてファイルを選択</span>{' '}
                  またはドラッグ＆ドロップ
                </p>
                <p className="text-xs text-gray-500">Excel (.xlsx, .xls)</p>
                {selectedFile && (
                  <p className="mt-2 text-sm text-blue-600 font-medium">
                    {selectedFile.name}
                  </p>
                )}
              </div>
              <input
                type="file"
                className="hidden"
                accept=".xlsx,.xls"
                onChange={handleFileSelect}
              />
            </label>
          </div>

          {/* Upload Button */}
          <div className="space-y-2">
            <button
              onClick={handleUpload}
              disabled={!selectedFile || loading}
              className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  処理中... お待ちください
                </>
              ) : (
                <>
                  <ArrowUpTrayIcon className="h-4 w-4 mr-2" />
                  インポート開始
                </>
              )}
            </button>

            {/* Loading Progress Indicator */}
            {loading && (
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{width: '100%'}}></div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <XCircleIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">エラー</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Success Result */}
      {result && result.success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex">
            <CheckCircleIcon className="h-5 w-5 text-green-400" />
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-green-800">
                インポート成功
              </h3>
              <div className="mt-2 text-sm text-green-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>新規作成: {result.created}件</li>
                  <li>更新: {result.updated}件</li>
                  <li>合計処理: {result.total_processed}件</li>
                </ul>
              </div>

              {result.errors.length > 0 && (
                <div className="mt-3">
                  <h4 className="text-sm font-medium text-yellow-800">
                    エラー ({result.errors.length}件):
                  </h4>
                  <ul className="mt-1 text-xs text-yellow-700 space-y-1">
                    {result.errors.map((err, idx) => (
                      <li key={idx}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          インポート手順
        </h3>
        <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
          <li>上のボタンからテンプレートをダウンロードしてください</li>
          <li>
            Excelファイルにデータを入力してください（ヘッダー行は変更しないでください）
          </li>
          <li>完成したExcelファイルをアップロードしてください</li>
          <li>
            派遣元IDが既に存在する場合は更新、存在しない場合は新規作成されます
          </li>
        </ol>

        <div className="mt-4 p-4 bg-yellow-50 rounded-md">
          <p className="text-sm text-yellow-800">
            <strong>注意:</strong>{' '}
            大量のデータをインポートする場合は時間がかかる場合があります。
          </p>
        </div>
      </div>
    </div>
  );
};

export default ImportData;
