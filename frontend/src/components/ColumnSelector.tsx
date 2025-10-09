import React, { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { EyeIcon, EyeSlashIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';

interface Column {
  key: string;
  label: string;
}

interface ColumnSelectorProps {
  columns: Column[];
  visibleColumns: Record<string, boolean>;
  onToggleColumn: (columnKey: string) => void;
  onToggleAll: (visible: boolean) => void;
}

export const ColumnSelector: React.FC<ColumnSelectorProps> = ({
  columns,
  visibleColumns,
  onToggleColumn,
  onToggleAll,
}) => {
  const visibleCount = Object.values(visibleColumns).filter(Boolean).length;
  const allVisible = visibleCount === columns.length;

  return (
    <Menu as="div" className="relative inline-block text-left">
      <div>
        <Menu.Button className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 hover:bg-slate-50 hover:ring-slate-300 transition">
          <AdjustmentsHorizontalIcon className="h-5 w-5 text-slate-500" />
          列表示
          <span className="ml-1 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700">
            {visibleCount}/{columns.length}
          </span>
        </Menu.Button>
      </div>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Item>
          {() => (
            <div className="absolute right-0 z-10 mt-2 w-80 origin-top-right rounded-2xl bg-white shadow-2xl ring-1 ring-black ring-opacity-5 focus:outline-none">
              <div className="p-4">
                <div className="flex items-center justify-between mb-3 pb-3 border-b border-slate-200">
                  <h3 className="text-sm font-bold text-slate-900">表示する列を選択</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => onToggleAll(true)}
                      className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 px-2 py-1 rounded hover:bg-indigo-50 transition"
                    >
                      全て表示
                    </button>
                    <button
                      onClick={() => onToggleAll(false)}
                      className="text-xs font-semibold text-slate-600 hover:text-slate-700 px-2 py-1 rounded hover:bg-slate-100 transition"
                    >
                      全て非表示
                    </button>
                  </div>
                </div>

                <div className="max-h-96 overflow-y-auto space-y-1">
                  {columns.map((column) => {
                    const isVisible = visibleColumns[column.key];
                    return (
                      <button
                        key={column.key}
                        onClick={() => onToggleColumn(column.key)}
                        className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                          isVisible
                            ? 'bg-indigo-50 text-indigo-900 hover:bg-indigo-100'
                            : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
                        }`}
                      >
                        <span className="flex items-center gap-2">
                          {isVisible ? (
                            <EyeIcon className="h-4 w-4 text-indigo-500" />
                          ) : (
                            <EyeSlashIcon className="h-4 w-4 text-slate-400" />
                          )}
                          {column.label}
                        </span>
                        <input
                          type="checkbox"
                          checked={isVisible}
                          onChange={() => {}}
                          className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                        />
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </Menu.Item>
      </Transition>
    </Menu>
  );
};

export default ColumnSelector;
