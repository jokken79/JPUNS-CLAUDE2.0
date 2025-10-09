import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

export type PageKey =
  | 'dashboard'
  | 'candidates'
  | 'pendingApproval'
  | 'employees'
  | 'employeesExtended'
  | 'importData'
  | 'factories'
  | 'timerCards'
  | 'salary'
  | 'requests';

type PageVisibilityState = Record<PageKey, boolean>;

type PageVisibilityContextValue = {
  visibility: PageVisibilityState;
  togglePage: (key: PageKey) => void;
  setPageVisibility: (key: PageKey, value: boolean) => void;
  isPageVisible: (key: PageKey) => boolean;
};

const STORAGE_KEY = 'page-visibility-settings';

const DEFAULT_VISIBILITY: PageVisibilityState = {
  dashboard: true,
  candidates: true,
  pendingApproval: true,
  employees: true,
  employeesExtended: true,
  importData: true,
  factories: true,
  timerCards: true,
  salary: true,
  requests: true,
};

const PageVisibilityContext = createContext<PageVisibilityContextValue | undefined>(
  undefined
);

export const PageVisibilityProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [visibility, setVisibility] = useState<PageVisibilityState>(DEFAULT_VISIBILITY);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) {
        return;
      }
      const parsed = JSON.parse(stored) as Partial<PageVisibilityState>;
      setVisibility((prev) => ({ ...prev, ...parsed }));
    } catch (error) {
      console.error('Failed to load page visibility preferences:', error);
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(visibility));
    } catch (error) {
      console.error('Failed to persist page visibility preferences:', error);
    }
  }, [visibility]);

  const value = useMemo<PageVisibilityContextValue>(
    () => ({
      visibility,
      togglePage: (key) =>
        setVisibility((prev) => ({
          ...prev,
          [key]: !prev[key],
        })),
      setPageVisibility: (key, value) =>
        setVisibility((prev) => ({
          ...prev,
          [key]: value,
        })),
      isPageVisible: (key) => visibility[key] ?? true,
    }),
    [visibility]
  );

  return (
    <PageVisibilityContext.Provider value={value}>
      {children}
    </PageVisibilityContext.Provider>
  );
};

export const usePageVisibility = () => {
  const context = useContext(PageVisibilityContext);
  if (!context) {
    throw new Error(
      'usePageVisibility must be used within a PageVisibilityProvider'
    );
  }
  return context;
};

export const pageVisibilityDefaults = DEFAULT_VISIBILITY;
