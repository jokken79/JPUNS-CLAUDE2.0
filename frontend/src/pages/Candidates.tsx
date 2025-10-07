import React from 'react';

const Candidates: React.FC = () => {
  return (
    <div className="h-full flex flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900">履歴書管理</h1>
        <p className="mt-1 text-sm text-gray-500">
          履歴書フォーム - 候補者情報の登録
        </p>
      </div>

      {/* Embed rirekisho.html in iframe */}
      <div className="flex-1 bg-white rounded-lg shadow-sm overflow-hidden">
        <iframe
          src="/templates/rirekisho.html"
          title="履歴書フォーム"
          className="w-full h-full border-0"
          style={{ minHeight: 'calc(100vh - 200px)' }}
        />
      </div>
    </div>
  );
};

export default Candidates;
